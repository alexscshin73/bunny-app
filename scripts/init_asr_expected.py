import argparse
import json
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create or refresh an ASR expected-manifest skeleton from eval-audio WAV files."
    )
    parser.add_argument(
        "audio_dir",
        nargs="?",
        default="eval-audio",
        help="Directory containing WAV files, typically eval-audio/.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("docs/asr_eval_expected.json"),
        help="Where to write the generated expected manifest.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing transcript text instead of preserving it.",
    )
    return parser.parse_args()


def collect_wavs(audio_dir: Path) -> list[Path]:
    return sorted(path for path in audio_dir.rglob("*.wav") if path.is_file())


def infer_language(relative_path: Path) -> str:
    first_part = relative_path.parts[0].lower() if relative_path.parts else ""
    if first_part in {"ko", "es"}:
        return first_part
    return ""


def load_existing(path: Path) -> dict[str, dict[str, str]]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def build_manifest(
    wavs: list[Path],
    audio_dir: Path,
    existing: dict[str, dict[str, str]],
    force: bool,
) -> dict[str, dict[str, str]]:
    manifest: dict[str, dict[str, str]] = {}

    for wav_path in wavs:
        relative_path = wav_path.relative_to(audio_dir).as_posix()
        relative_obj = Path(relative_path)
        language = infer_language(relative_obj)
        previous = existing.get(relative_path) or existing.get(wav_path.name) or {}

        text = ""
        if not force:
            text = str(previous.get("text", ""))

        manifest[relative_path] = {
            "language": language or str(previous.get("language", "")),
            "text": text,
        }

    return manifest


def main() -> None:
    args = parse_args()
    audio_dir = Path(args.audio_dir)
    if not audio_dir.exists():
        raise SystemExit(f"audio directory not found: {audio_dir}")

    wavs = collect_wavs(audio_dir)
    if not wavs:
        raise SystemExit(f"no WAV files found under: {audio_dir}")

    existing = load_existing(args.output)
    manifest = build_manifest(
        wavs=wavs,
        audio_dir=audio_dir,
        existing=existing,
        force=args.force,
    )

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    print(f"Wrote {len(manifest)} entries to {args.output}")


if __name__ == "__main__":
    main()
