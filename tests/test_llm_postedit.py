import httpx
import pytest

from app.services.llm_postedit import (
    FallbackTranslationPolisher,
    HeuristicTranslationPolisher,
    OpenAICompatibleTranslationPolisher,
    _build_user_prompt,
)


@pytest.mark.anyio
async def test_openai_compatible_polisher_returns_model_output() -> None:
    async def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path.endswith("/chat/completions")
        body = await request.aread()
        assert b"Draft translation" in body
        return httpx.Response(
            200,
            json={
                "choices": [
                    {
                        "message": {
                            "content": "Vamos a revisarlo.",
                        }
                    }
                ]
            },
        )

    class MockClient(httpx.AsyncClient):
        def __init__(self, *args, **kwargs):
            kwargs["transport"] = httpx.MockTransport(handler)
            super().__init__(*args, **kwargs)

    polisher = OpenAICompatibleTranslationPolisher(
        base_url="http://localhost:11434/v1",
        model="qwen2.5:7b-instruct",
        timeout_s=3.0,
        client_factory=MockClient,
    )

    polished = await polisher.polish_translation(
        source_text="자~ 봅시다",
        source_language="ko",
        target_language="es",
        draft_translation="Vamos, veamos.",
        conversation_history=[],
    )

    assert polished == "Vamos a revisarlo."


def test_build_user_prompt_contains_recent_context() -> None:
    prompt = _build_user_prompt(
        source_text="오늘 회의 시작합시다",
        source_language="ko",
        target_language="es",
        draft_translation="Empecemos la reunión de hoy.",
        conversation_history=[
            {
                "source_language": "ko",
                "source_text": "안녕하세요",
                "translations": {"es": "Hola"},
            }
        ],
    )

    assert "ko: 안녕하세요" in prompt
    assert "es: Hola" in prompt
    assert "Draft translation: Empecemos la reunión de hoy." in prompt


@pytest.mark.anyio
async def test_heuristic_polisher_improves_known_quality_phrase() -> None:
    polisher = HeuristicTranslationPolisher()

    polished = await polisher.polish_translation(
        source_text="번역 품질이 너무 낮죠.",
        source_language="ko",
        target_language="es",
        draft_translation="Las traducciones son muy bajas.",
        conversation_history=[],
    )

    assert polished == "La calidad de la traduccion es muy baja."


@pytest.mark.anyio
async def test_fallback_polisher_uses_heuristic_when_primary_is_unavailable() -> None:
    primary = OpenAICompatibleTranslationPolisher(
        base_url=None,
        model=None,
        timeout_s=1.0,
    )
    polisher = FallbackTranslationPolisher(
        primary=primary,
        fallback=HeuristicTranslationPolisher(),
    )

    polished = await polisher.polish_translation(
        source_text="번역 품질이 너무 낮죠.",
        source_language="ko",
        target_language="es",
        draft_translation="Las traducciones son muy bajas.",
        conversation_history=[],
    )

    assert polished == "La calidad de la traduccion es muy baja."
