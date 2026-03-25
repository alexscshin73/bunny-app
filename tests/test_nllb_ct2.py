from types import SimpleNamespace

import pytest

from app.services.translate.nllb_ct2 import (
    NllbCTranslate2Translator,
    _max_decoding_length_for,
    detect_text_language,
)


class FakeTokenizer:
    def __init__(self) -> None:
        self.src_lang = "eng_Latn"

    def encode(self, text: str) -> list[str]:
        return text.split()

    def convert_ids_to_tokens(self, values: list[str]) -> list[str]:
        return values

    def convert_tokens_to_ids(self, values: list[str]) -> list[str]:
        return values

    def decode(self, values: list[str], skip_special_tokens: bool = True) -> str:
        return " ".join(values)


class FakeTranslator:
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def translate_batch(
        self,
        batch: list[list[str]],
        target_prefix: list[list[str]],
        beam_size: int,
        repetition_penalty: float | None = None,
        no_repeat_ngram_size: int | None = None,
        max_decoding_length: int | None = None,
    ) -> list[SimpleNamespace]:
        self.calls.append(
            {
                "beam_size": beam_size,
                "batch_size": len(batch),
                "max_decoding_length": max_decoding_length,
            }
        )
        assert beam_size in {2, 3, 4, 5}
        assert repetition_penalty == 1.18
        assert no_repeat_ngram_size == 3
        assert max_decoding_length is not None
        return [
            SimpleNamespace(hypotheses=[[prefix[0], f"{prefix[0]}::{' '.join(tokens)}"]])
            for tokens, prefix in zip(batch, target_prefix, strict=True)
        ]


def test_detect_text_language_prefers_hangul_and_spanish_markers() -> None:
    assert detect_text_language("이상한데?") == "ko"
    assert detect_text_language("¿como estas?") == "es"
    assert detect_text_language("bien, muy bien, todo bien") == "es"


@pytest.mark.anyio
async def test_nllb_translator_translates_all_targets_with_fake_runtime() -> None:
    fake_runtime = FakeTranslator()
    translator = NllbCTranslate2Translator(
        model_path="/tmp/model",
        tokenizer_path="/tmp/tokenizer",
        default_targets=["ko", "es"],
    )
    translator._translator = fake_runtime
    translator._tokenizer = FakeTokenizer()

    translations = await translator.translate_all(
        text="hello there",
        source_language="es",
        target_languages=["ko", "es"],
    )

    assert translations["es"] == "hello there"
    assert translations["ko"] == "kor_Hang::hello there"
    assert fake_runtime.calls[0]["beam_size"] == 4


@pytest.mark.anyio
async def test_nllb_translator_uses_faster_realtime_mode_and_caches_results() -> None:
    fake_runtime = FakeTranslator()
    translator = NllbCTranslate2Translator(
        model_path="/tmp/model",
        tokenizer_path="/tmp/tokenizer",
        default_targets=["ko", "es"],
    )
    translator._translator = fake_runtime
    translator._tokenizer = FakeTokenizer()

    first = await translator.translate_all(
        text="hola amigos",
        source_language="es",
        target_languages=["ko", "es"],
        mode="realtime",
    )
    second = await translator.translate_all(
        text="hola amigos",
        source_language="es",
        target_languages=["ko", "es"],
        mode="realtime",
    )

    assert first == second
    assert len(fake_runtime.calls) == 1
    assert fake_runtime.calls[0]["beam_size"] == 2


def test_nllb_status_reports_missing_local_model() -> None:
    translator = NllbCTranslate2Translator(
        model_path="/missing/model",
        tokenizer_path="/missing/tokenizer",
    )

    status = translator.status()

    assert status.engine == "nllb_ct2"
    assert status.ready is False
    assert status.details["model_found"] is False


def test_max_decoding_length_shrinks_for_short_inputs() -> None:
    assert _max_decoding_length_for(["안녕"]) == 8
    assert _max_decoding_length_for(["왜냐하면", "요즘", "못", "잤거든요"]) == 12
    assert _max_decoding_length_for(["그리고"] * 7) == 18
