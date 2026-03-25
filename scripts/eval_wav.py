import argparse
import asyncio
import json
import re
import wave
from collections import defaultdict
from datetime import UTC, datetime
from difflib import SequenceMatcher
from pathlib import Path

from app.config import get_settings
from app.services.asr.whisper_cpp import WhisperCppStreamingAsr
from app.services.pipeline import build_translator


def parse_args() -> argparse.Namespace:
    settings = get_settings()
    parser = argparse.ArgumentParser(
        description="Evaluate local WAV files with Bunny App ASR and translation."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        default=["test-audio"],
        help="WAV files or directories containing WAV files.",
    )
    parser.add_argument(
        "--language",
        default="auto",
        choices=["auto", "ko", "es"],
        help="Language hint to pass into ASR.",
    )
    parser.add_argument(
        "--expected",
        type=Path,
        help="Optional JSON file mapping filename to expected text/language.",
    )
    parser.add_argument(
        "--model-path",
        action="append",
        type=Path,
        help=(
            "Repeatable whisper model path override. If omitted, uses "
            "BUNNY_WHISPER_MODEL_PATH from the environment."
        ),
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Print JSON instead of plain text.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Optional path to write the structured report JSON.",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Print aggregate summary by model after file reports.",
    )
    parser.add_argument(
        "--no-translate",
        action="store_true",
        help="Skip translation output to focus on ASR-only evaluation.",
    )
    parser.add_argument(
        "--use-gpu",
        action="store_true",
        help="Use whisper.cpp GPU path. Default is CPU for stable offline evaluation.",
    )
    parser.epilog = (
        "Expected JSON entries may be keyed by file name or by a relative path such as "
        "\"ko/check_01.wav\". Each entry can include {\"language\": \"ko\", \"text\": \"...\"}."
        if settings.whisper_model_path
        else None
    )
    return parser.parse_args()


def collect_wavs(raw_paths: list[str]) -> list[Path]:
    wavs: list[Path] = []
    for raw_path in raw_paths:
        path = Path(raw_path)
        if path.is_dir():
            wavs.extend(sorted(path.rglob("*.wav")))
            continue
        if path.suffix.lower() == ".wav" and path.exists():
            wavs.append(path)
    return wavs


def load_expected(path: Path | None) -> dict[str, dict[str, str]]:
    if path is None:
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def expected_entry_for_path(
    expected_map: dict[str, dict[str, str]],
    path: Path,
) -> dict[str, str] | None:
    candidates = [path.name, path.as_posix()]
    try:
        candidates.append(path.resolve().relative_to(Path.cwd()).as_posix())
    except Exception:
        pass

    for candidate in candidates:
        entry = expected_map.get(candidate)
        if entry:
            return entry
    return None


def resolve_model_paths(raw_model_paths: list[Path] | None) -> list[Path]:
    settings = get_settings()
    if raw_model_paths:
        return [path.expanduser() for path in raw_model_paths]

    if settings.whisper_model_path:
        return [Path(settings.whisper_model_path).expanduser()]

    raise SystemExit(
        "No model path available. Pass --model-path or set BUNNY_WHISPER_MODEL_PATH."
    )


def read_wav(path: Path) -> tuple[bytes, int, float]:
    with wave.open(str(path), "rb") as wav_file:
        channels = wav_file.getnchannels()
        sample_width = wav_file.getsampwidth()
        sample_rate = wav_file.getframerate()
        pcm = wav_file.readframes(wav_file.getnframes())

    if channels != 1 or sample_width != 2:
        raise RuntimeError(
            f"{path.name}: expected 16-bit mono WAV, got channels={channels}, sample_width={sample_width}"
        )

    duration_seconds = len(pcm) / max(sample_rate * sample_width, 1)
    return pcm, sample_rate, duration_seconds


def normalize_text(text: str) -> str:
    lowered = text.casefold().strip()
    collapsed = re.sub(r"\s+", " ", lowered)
    return collapsed


def compare_text(expected: str, actual: str) -> dict[str, float | bool]:
    expected_normalized = normalize_text(expected)
    actual_normalized = normalize_text(actual)
    ratio = round(SequenceMatcher(None, expected_normalized, actual_normalized).ratio(), 3)
    contains = expected_normalized in actual_normalized or actual_normalized in expected_normalized
    return {"similarity": ratio, "contains": contains}


async def evaluate_file(
    path: Path,
    language: str,
    use_gpu: bool,
    expected_map: dict[str, dict[str, str]],
    model_path: Path,
    include_translations: bool,
) -> dict[str, object]:
    settings = get_settings()
    asr = WhisperCppStreamingAsr(
        binary_path=settings.whisper_cpp_binary,
        model_path=str(model_path),
        default_language=settings.whisper_language,
        no_gpu=not use_gpu,
        use_vad=False,
        vad_model_path=settings.whisper_vad_model_path,
    )
    translator = build_translator(settings) if include_translations else None

    pcm, sample_rate, duration_seconds = read_wav(path)
    result = await asr.transcribe_chunk(
        pcm_chunk=pcm,
        sample_rate=sample_rate,
        language=language,
        is_final=True,
    )
    translations = {}
    if translator:
        translations = await translator.translate_all(
            text=result.text,
            source_language=result.language,
            target_languages=settings.translation_targets,
            mode="quality",
        )

    report: dict[str, object] = {
        "model": model_path.name,
        "model_path": str(model_path),
        "file": path.name,
        "path": path.as_posix(),
        "duration_seconds": round(duration_seconds, 2),
        "detected_language": result.language,
        "text": result.text,
        "translations": translations,
    }

    expected = expected_entry_for_path(expected_map, path)
    if expected:
        comparison: dict[str, object] = {}
        expected_language = expected.get("language")
        expected_text = expected.get("text")
        if expected_language:
            comparison["language_match"] = expected_language == result.language
        if expected_text:
            comparison |= compare_text(expected_text, result.text)
        report["expected"] = expected
        report["comparison"] = comparison

    return report


def print_human_report(report: dict[str, object]) -> None:
    print(f"MODEL: {report['model']}")
    print(f"FILE: {report['file']}")
    print(
        f"DURATION: {report['duration_seconds']}s | DETECTED: {report['detected_language']}"
    )
    print(f"TEXT: {report['text']}")
    if report["translations"]:
        print(f"TRANSLATIONS: {json.dumps(report['translations'], ensure_ascii=False)}")
    if "comparison" in report:
        print(f"COMPARISON: {json.dumps(report['comparison'], ensure_ascii=False)}")
    print()


def build_summary(reports: list[dict[str, object]]) -> list[dict[str, object]]:
    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for report in reports:
        grouped[str(report["model"])].append(report)

    summary: list[dict[str, object]] = []
    for model, group in sorted(grouped.items()):
        similarity_values: list[float] = []
        contains_hits = 0
        language_matches = 0
        expected_count = 0
        unknown_count = 0
        empty_text_count = 0

        for report in group:
            detected_language = str(report.get("detected_language", ""))
            text = str(report.get("text", "")).strip()
            if detected_language in {"", "unknown"}:
                unknown_count += 1
            if not text:
                empty_text_count += 1

            comparison = report.get("comparison")
            if not isinstance(comparison, dict):
                continue

            expected_count += 1
            similarity = comparison.get("similarity")
            if isinstance(similarity, (int, float)):
                similarity_values.append(float(similarity))
            if comparison.get("contains") is True:
                contains_hits += 1
            if comparison.get("language_match") is True:
                language_matches += 1

        summary.append(
            {
                "model": model,
                "files": len(group),
                "expected_files": expected_count,
                "avg_similarity": round(sum(similarity_values) / len(similarity_values), 3)
                if similarity_values
                else None,
                "contains_rate": round(contains_hits / expected_count, 3) if expected_count else None,
                "language_match_rate": round(language_matches / expected_count, 3)
                if expected_count
                else None,
                "unknown_count": unknown_count,
                "empty_text_count": empty_text_count,
            }
        )

    return summary


def print_human_summary(summary: list[dict[str, object]]) -> None:
    print("SUMMARY")
    for item in summary:
        parts = [
            f"model={item['model']}",
            f"files={item['files']}",
            f"expected={item['expected_files']}",
            f"avg_similarity={item['avg_similarity']}",
            f"contains_rate={item['contains_rate']}",
            f"language_match_rate={item['language_match_rate']}",
            f"unknown={item['unknown_count']}",
            f"empty={item['empty_text_count']}",
        ]
        print(" - " + " | ".join(parts))


async def main() -> None:
    args = parse_args()
    wavs = collect_wavs(args.paths)
    if not wavs:
        raise SystemExit("No WAV files found.")

    expected_map = load_expected(args.expected)
    model_paths = resolve_model_paths(args.model_path)
    reports = []
    for model_path in model_paths:
        for wav_path in wavs:
            reports.append(
                await evaluate_file(
                    path=wav_path,
                    language=args.language,
                    use_gpu=args.use_gpu,
                    expected_map=expected_map,
                    model_path=model_path,
                    include_translations=not args.no_translate,
                )
            )

    summary = build_summary(reports)
    metadata = {
        "created_at": datetime.now(UTC).isoformat(),
        "language": args.language,
        "use_gpu": args.use_gpu,
        "include_translations": not args.no_translate,
        "paths": [str(Path(raw_path)) for raw_path in args.paths],
        "expected": str(args.expected) if args.expected else None,
        "models": [str(path) for path in model_paths],
    }
    payload: dict[str, object] = {"reports": reports}
    payload["metadata"] = metadata
    if args.summary:
        payload["summary"] = summary

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return

    for report in reports:
        print_human_report(report)

    if args.summary:
        print_human_summary(summary)


if __name__ == "__main__":
    asyncio.run(main())
