from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]


def _load_module(path: Path, module_name: str):
    spec = spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Unable to load module from {path}")
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_init_asr_expected_build_manifest_preserves_existing_text() -> None:
    module = _load_module(ROOT_DIR / "scripts" / "init_asr_expected.py", "init_asr_expected")

    audio_dir = ROOT_DIR / "eval-audio"
    wavs = [
        audio_dir / "ko" / "check_01.wav",
        audio_dir / "es" / "check_02.wav",
    ]
    existing = {
        "ko/check_01.wav": {"language": "ko", "text": "기존 문장"},
    }

    manifest = module.build_manifest(
        wavs=wavs,
        audio_dir=audio_dir,
        existing=existing,
        force=False,
    )

    assert manifest["ko/check_01.wav"]["language"] == "ko"
    assert manifest["ko/check_01.wav"]["text"] == "기존 문장"
    assert manifest["es/check_02.wav"]["language"] == "es"
    assert manifest["es/check_02.wav"]["text"] == ""


def test_init_asr_expected_force_resets_existing_text() -> None:
    module = _load_module(ROOT_DIR / "scripts" / "init_asr_expected.py", "init_asr_expected_force")

    audio_dir = ROOT_DIR / "eval-audio"
    wavs = [audio_dir / "ko" / "check_01.wav"]
    existing = {
        "ko/check_01.wav": {"language": "ko", "text": "기존 문장"},
    }

    manifest = module.build_manifest(
        wavs=wavs,
        audio_dir=audio_dir,
        existing=existing,
        force=True,
    )

    assert manifest["ko/check_01.wav"]["language"] == "ko"
    assert manifest["ko/check_01.wav"]["text"] == ""


def test_compare_asr_reports_prefers_candidate_with_higher_similarity() -> None:
    module = _load_module(ROOT_DIR / "scripts" / "compare_asr_reports.py", "compare_asr_reports")

    baseline_payload = {
        "source": "baseline.json",
        "reports": [
            {
                "model": "ggml-large-v3-turbo.bin",
                "path": "eval-audio/ko/check_01.wav",
                "detected_language": "ko",
                "text": "보정이 안돼",
                "comparison": {"similarity": 0.42, "contains": False, "language_match": True},
            }
        ],
    }
    candidate_payload = {
        "source": "candidate.json",
        "reports": [
            {
                "model": "ggml-large-v3-turbo.bin",
                "path": "eval-audio/ko/check_01.wav",
                "detected_language": "ko",
                "text": "보정이 안돼 보정이",
                "comparison": {"similarity": 0.88, "contains": True, "language_match": True},
            }
        ],
    }

    result = module.compare_reports(baseline_payload, candidate_payload)

    assert result["shared_files"] == 1
    assert result["candidate_wins"] == 1
    assert result["baseline_wins"] == 0
    assert result["files"][0]["winner"] == "candidate"
    assert result["files"][0]["candidate_text"] == "보정이 안돼 보정이"
