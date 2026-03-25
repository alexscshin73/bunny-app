from app.services.translation_guardrails import canonicalize_source_text, stabilize_translation_text, stabilize_translations
from app.services.translate.base import TranslatorBackendStatus
from app.services.translate.guardrailed import GuardrailedTranslator


def test_stabilize_translation_text_fixes_korean_greeting() -> None:
    stabilized = stabilize_translation_text(
        source_text="안녕하세요",
        source_language="ko",
        target_language="es",
        translation_text="Hola, por favor.",
    )

    assert stabilized == "Hola."


def test_stabilize_translation_text_fixes_spanish_thanks() -> None:
    stabilized = stabilize_translation_text(
        source_text="Muchas gracias",
        source_language="es",
        target_language="ko",
        translation_text="많은 감사합니다.",
    )

    assert stabilized == "감사합니다."


def test_stabilize_translation_text_softens_ambiguous_spanish_casual_korean_output() -> None:
    stabilized = stabilize_translation_text(
        source_text="No tengo tiempo ahora",
        source_language="es",
        target_language="ko",
        translation_text="지금 시간 없어",
    )

    assert stabilized == "지금 시간 없어요."


def test_stabilize_translation_text_keeps_explicit_tu_source_as_is() -> None:
    stabilized = stabilize_translation_text(
        source_text="Gracias por tu ayuda",
        source_language="es",
        target_language="ko",
        translation_text="도와줘서 고마워",
    )

    assert stabilized == "도와줘서 고마워"


def test_stabilize_translation_text_fixes_spanish_arrival_time_phrase() -> None:
    stabilized = stabilize_translation_text(
        source_text="Llegaré en diez minutos",
        source_language="es",
        target_language="ko",
        translation_text="10분 안에 도착할게요",
    )

    assert stabilized == "10분 후 도착해요."


def test_stabilize_translation_text_applies_spanish_to_korean_exact_override() -> None:
    stabilized = stabilize_translation_text(
        source_text="La cuenta, por favor",
        source_language="es",
        target_language="ko",
        translation_text="계산해 주세요",
    )

    assert stabilized == "계산서 주세요"


def test_stabilize_translation_text_applies_evaluated_zero_case_override() -> None:
    stabilized = stabilize_translation_text(
        source_text="Eso suena bien",
        source_language="es",
        target_language="ko",
        translation_text="잘 들리네요",
    )

    assert stabilized == "그거 좋네"


def test_stabilize_translation_text_maps_estoy_en_problemas_to_state_phrase() -> None:
    stabilized = stabilize_translation_text(
        source_text="Estoy en problemas",
        source_language="es",
        target_language="ko",
        translation_text="나는 문제들 안에 있어",
    )

    assert stabilized == "문제 생겼어요."


def test_stabilize_translation_text_maps_estoy_en_reunion_to_in_progress_phrase() -> None:
    stabilized = stabilize_translation_text(
        source_text="Estoy en una reunión",
        source_language="es",
        target_language="ko",
        translation_text="나는 회의 안에 있어",
    )

    assert stabilized == "회의 중이에요."


def test_stabilize_translation_text_maps_estoy_en_clase_to_in_progress_phrase() -> None:
    stabilized = stabilize_translation_text(
        source_text="Estoy en clase",
        source_language="es",
        target_language="ko",
        translation_text="나는 교실에 있어",
    )

    assert stabilized == "수업 중이에요."


def test_canonicalize_source_text_restores_common_spanish_accents() -> None:
    canonical = canonicalize_source_text("como estas?", language="es")

    assert canonical == "¿Cómo estás?"


def test_canonicalize_source_text_normalizes_common_korean_greeting() -> None:
    canonical = canonicalize_source_text("잘지내시나요?", language="ko")

    assert canonical == "잘 지내시나요?"


def test_stabilize_translations_preserves_source_language_entry() -> None:
    stabilized = stabilize_translations(
        source_text="안녕하세요",
        source_language="ko",
        translations={"ko": "안녕하세요", "es": "Hola, por favor."},
    )

    assert stabilized == {"ko": "안녕하세요", "es": "Hola."}


def test_stabilize_translation_text_fixes_korean_how_are_you_phrase() -> None:
    stabilized = stabilize_translation_text(
        source_text="잘지내시나요?",
        source_language="ko",
        target_language="es",
        translation_text="¿Quieres hacerlo bien?",
    )

    assert stabilized == "¿Cómo estás?"


def test_stabilize_translation_text_applies_korean_to_spanish_exact_override_for_banmal_request() -> None:
    stabilized = stabilize_translation_text(
        source_text="문자 보내줘",
        source_language="ko",
        target_language="es",
        translation_text="Envíeme un mensaje.",
    )

    assert stabilized == "Mándame un mensaje"


def test_stabilize_translation_text_applies_korean_to_spanish_exact_override_for_farewell() -> None:
    stabilized = stabilize_translation_text(
        source_text="좋은 하루 보내",
        source_language="ko",
        target_language="es",
        translation_text="Tienes un buen día.",
    )

    assert stabilized == "Que tengas buen día"


def test_stabilize_translation_text_applies_korean_to_spanish_exact_override_for_travel_warning() -> None:
    stabilized = stabilize_translation_text(
        source_text="운전 조심해",
        source_language="ko",
        target_language="es",
        translation_text="Hay que conducir con cuidado.",
    )

    assert stabilized == "Ten cuidado al conducir"


def test_stabilize_translation_text_rewrites_generic_korean_low_appraisal() -> None:
    stabilized = stabilize_translation_text(
        source_text="별로다",
        source_language="ko",
        target_language="es",
        translation_text="No es así.",
    )

    assert stabilized == "No está muy bien."


def test_stabilize_translation_text_rewrites_object_low_appraisal() -> None:
    stabilized = stabilize_translation_text(
        source_text="이거 별로야",
        source_language="ko",
        target_language="es",
        translation_text="No es así.",
    )

    assert stabilized == "Esto no está muy bien."


import pytest


class _EchoTranslator:
    def status(self) -> TranslatorBackendStatus:
        return TranslatorBackendStatus(engine="echo", ready=True, details={})

    async def translate_all(self, text: str, source_language: str, target_languages: list[str], *, mode: str = "quality") -> dict[str, str]:
        return {
            target: text if target == source_language else "Hola, por favor." if target == "es" else "지금과 같이요?"
            for target in target_languages
        }


@pytest.mark.anyio
async def test_guardrailed_translator_stabilizes_any_backend_output() -> None:
    translator = GuardrailedTranslator(_EchoTranslator())

    translations = await translator.translate_all(
        text="안녕하세요.",
        source_language="ko",
        target_languages=["ko", "es"],
    )

    assert translations["es"] == "Hola."
