from pathlib import Path

from app.services.asr.whisper_cpp import (
    WhisperCppStreamingAsr,
    infer_best_ko_es_language,
    parse_detected_language_output,
    select_best_ko_es_result,
    should_retry_restricted_auto,
)


def test_auto_language_prefers_spanish_text_over_cjk_noise() -> None:
    language, text = select_best_ko_es_result(
        {
            "ko": "解决完毕了",
            "es": "Bien, muy bien, todo bien.",
        }
    )

    assert language == "es"
    assert text == "Bien, muy bien, todo bien."


def test_auto_language_prefers_korean_when_hangul_is_present() -> None:
    language, text = select_best_ko_es_result(
        {
            "ko": "해결이 끝났어",
            "es": "haegyeol-i kkeutnass-eo",
        }
    )

    assert language == "ko"
    assert text == "해결이 끝났어"


def test_auto_language_prefers_real_spanish_over_hangul_gibberish() -> None:
    language, text = select_best_ko_es_result(
        {
            "ko": (
                "이 3개의 단어는, 택, 렘, 팩, 렘이 필요한 것입니다. "
                "가장 중요한 것은, 제 cell phone에 놓지 않게 일으켜주세요. "
                "이 방법은 디자인 UX UI 테스터드 소프트 웹을 만들고, 잘 알아보겠습니다."
            ),
            "es": (
                "Estos son los 3 pasos que tienes que seguir si quieres un trabajo en tech, "
                "remoto y bien pagado. Número 1, lo más importante, deja de escrolear "
                "en tu celular y actúa."
            ),
        }
    )

    assert language == "es"
    assert text.startswith("Estos son los 3 pasos")


def test_parse_detected_language_output_reads_whisper_cli_line() -> None:
    language, probability = parse_detected_language_output(
        "whisper_full_with_state: auto-detected language: es (p = 0.998967)"
    )

    assert language == "es"
    assert probability == 0.998967


def test_infer_best_ko_es_language_from_single_transcript() -> None:
    assert infer_best_ko_es_language("안녕하세요. 오늘 회의를 시작하겠습니다.") == "ko"
    assert infer_best_ko_es_language("Hola, buenos dias. Vamos a empezar la reunion.") == "es"


def test_auto_language_retries_when_unsupported_script_is_present() -> None:
    assert should_retry_restricted_auto("スペインの手を張り替えて") is True
    assert should_retry_restricted_auto("நான் வந்துவிட்டேன்.") is True


def test_auto_language_drops_outputs_outside_ko_es_scripts() -> None:
    language, text = select_best_ko_es_result(
        {
            "ko": "நான் வந்துவிட்டேன்.",
            "es": "スペインの手を張り替えて",
        }
    )

    assert language == ""
    assert text == ""


def test_auto_language_prefers_supported_text_over_unsupported_script() -> None:
    language, text = select_best_ko_es_result(
        {
            "ko": "어떻게 들리는지",
            "es": "スペインの手を張り替えて",
        }
    )

    assert language == "ko"
    assert text == "어떻게 들리는지"


def test_auto_language_prefers_real_korean_over_known_broadcast_hallucination() -> None:
    language, text = select_best_ko_es_result(
        {
            "ko": "두 마리 잘 들리나요?",
            "es": "MBC 뉴스 김성현입니다.",
        }
    )

    assert language == "ko"
    assert text == "두 마리 잘 들리나요?"


def test_transcribe_command_uses_partial_and_final_beam_profiles() -> None:
    asr = WhisperCppStreamingAsr(
        binary_path="/opt/homebrew/bin/whisper-cli",
        model_path="/tmp/model.bin",
        default_language="ko",
        no_gpu=True,
        suppress_non_speech=True,
        no_fallback=True,
        threads=6,
        processors=2,
        partial_beam_size=2,
        final_beam_size=5,
    )

    partial_command = asr._transcribe_command(
        binary_path=Path("/opt/homebrew/bin/whisper-cli"),
        model_path=Path("/tmp/model.bin"),
        wav_path=Path("/tmp/chunk.wav"),
        out_prefix=Path("/tmp/chunk"),
        language="ko",
        is_final=False,
    )
    final_command = asr._transcribe_command(
        binary_path=Path("/opt/homebrew/bin/whisper-cli"),
        model_path=Path("/tmp/model.bin"),
        wav_path=Path("/tmp/chunk.wav"),
        out_prefix=Path("/tmp/chunk"),
        language="ko",
        is_final=True,
    )

    assert partial_command[0] == "/opt/homebrew/bin/whisper-cli"
    assert ["-t", "6"] == partial_command[9:11]
    assert ["-p", "2"] == partial_command[11:13]
    assert ["-bs", "2"] == partial_command[13:15]
    assert ["-bs", "5"] == final_command[13:15]
    assert partial_command[-2:] == ["-l", "ko"]
