import pytest

from app.models.events import ClientControlEvent
from app.services.asr.base import AsrBackendStatus, AsrResult, StreamingAsr
from app.services.asr.mock import MockStreamingAsr
from app.services.llm_postedit import TranslationPolisher, TranslationPolisherStatus
from app.services.session import RealtimeSession
from app.services.translate.base import Translator, TranslatorBackendStatus
from app.services.translate.mock import MockTranslator


class HintRecordingAsr(StreamingAsr):
    def __init__(self) -> None:
        self.languages: list[str] = []

    def status(self) -> AsrBackendStatus:
        return AsrBackendStatus(engine="hint-recorder", ready=True, details={})

    async def transcribe_chunk(
        self,
        pcm_chunk: bytes,
        sample_rate: int,
        language: str,
        is_final: bool,
    ) -> AsrResult:
        self.languages.append(language)
        effective_language = "es" if language == "auto" else language
        return AsrResult(
            text=f"{effective_language}-{len(self.languages)}",
            language=effective_language,
            is_final=is_final,
        )


class SequenceAsr(StreamingAsr):
    def __init__(self, results: list[AsrResult]) -> None:
        self.results = results
        self.index = 0

    def status(self) -> AsrBackendStatus:
        return AsrBackendStatus(engine="sequence", ready=True, details={})

    async def transcribe_chunk(
        self,
        pcm_chunk: bytes,
        sample_rate: int,
        language: str,
        is_final: bool,
    ) -> AsrResult:
        result = self.results[self.index]
        self.index += 1
        return result


class RecordingChunkAsr(StreamingAsr):
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def status(self) -> AsrBackendStatus:
        return AsrBackendStatus(engine="recording-chunk", ready=True, details={})

    async def transcribe_chunk(
        self,
        pcm_chunk: bytes,
        sample_rate: int,
        language: str,
        is_final: bool,
    ) -> AsrResult:
        self.calls.append(
            {
                "bytes": len(pcm_chunk),
                "sample_rate": sample_rate,
                "language": language,
                "is_final": is_final,
            }
        )
        return AsrResult(
            text=f"{'final' if is_final else 'partial'}-{len(pcm_chunk)}",
            language="ko",
            is_final=is_final,
        )


class MockPolisher(TranslationPolisher):
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def status(self) -> TranslationPolisherStatus:
        return TranslationPolisherStatus(engine="mock-polisher", ready=True, details={})

    async def polish_translation(
        self,
        source_text: str,
        source_language: str,
        target_language: str,
        draft_translation: str,
        conversation_history: list[dict[str, object]],
    ) -> str:
        self.calls.append(
            {
                "source_text": source_text,
                "source_language": source_language,
                "target_language": target_language,
                "draft_translation": draft_translation,
                "conversation_history": conversation_history,
            }
        )
        return f"[polished {target_language}] {draft_translation}"


class SequenceTranslator(Translator):
    def __init__(self, outputs: list[dict[str, str]]) -> None:
        self.outputs = outputs
        self.index = 0

    def status(self) -> TranslatorBackendStatus:
        return TranslatorBackendStatus(engine="sequence-translator", ready=True, details={})

    async def translate_all(
        self,
        text: str,
        source_language: str,
        target_languages: list[str],
        *,
        mode: str = "quality",
    ) -> dict[str, str]:
        output = dict(self.outputs[self.index])
        self.index += 1
        for target in target_languages:
            output.setdefault(target, text if target == source_language else f"[{source_language}->{target}] {text}")
        return output


class RecordingTranslator(Translator):
    def __init__(self) -> None:
        self.calls: list[dict[str, object]] = []

    def status(self) -> TranslatorBackendStatus:
        return TranslatorBackendStatus(engine="recording-translator", ready=True, details={})

    async def translate_all(
        self,
        text: str,
        source_language: str,
        target_languages: list[str],
        *,
        mode: str = "quality",
    ) -> dict[str, str]:
        self.calls.append(
            {
                "text": text,
                "source_language": source_language,
                "target_languages": list(target_languages),
                "mode": mode,
            }
        )
        return {
            target: text if target == source_language else f"[{source_language}->{target}] {text}"
            for target in target_languages
        }


@pytest.mark.anyio
async def test_stop_promotes_last_partial_to_final_when_buffer_is_empty() -> None:
    session = RealtimeSession(
        asr=MockStreamingAsr(),
        translator=MockTranslator(default_targets=["ko", "es"]),
        polisher=None,
        target_languages=["ko", "es"],
        vad_enabled=False,
        segment_emit_ms=0,
        segment_emit_bytes=4,
    )

    partial_events = await session.push_audio(b"\x00\x01" * 2)
    stop_events = await session.handle_control(ClientControlEvent(type="stop"))

    assert [event.type for event in partial_events] == ["partial", "translation"]
    assert [event.type for event in stop_events] == ["final", "translation", "stats"]
    assert stop_events[0].payload["text"] == partial_events[0].payload["text"]
    assert stop_events[1].payload["is_final"] is True
    assert stop_events[2].payload["buffered_audio_bytes"] == 0


@pytest.mark.anyio
async def test_stop_flushes_buffer_to_final_with_translation_and_stats() -> None:
    session = RealtimeSession(
        asr=MockStreamingAsr(),
        translator=MockTranslator(default_targets=["ko", "es"]),
        polisher=None,
        target_languages=["ko", "es"],
        vad_enabled=False,
        segment_emit_ms=0,
        segment_emit_bytes=100,
    )

    partial_events = await session.push_audio(b"\x00\x01" * 10)
    stop_events = await session.handle_control(ClientControlEvent(type="stop"))

    assert partial_events == []
    assert [event.type for event in stop_events] == ["final", "translation", "stats"]
    assert stop_events[0].payload["language"] == "ko"
    assert stop_events[1].payload["translations"]["es"].startswith("[ko->es]")
    assert stop_events[2].payload["total_audio_bytes"] == 20


@pytest.mark.anyio
async def test_stop_flushes_nonverbal_final_without_translation() -> None:
    translator = RecordingTranslator()
    session = RealtimeSession(
        asr=SequenceAsr([AsrResult(text="🍺", language="ko", is_final=True)]),
        translator=translator,
        polisher=None,
        target_languages=["ko", "es"],
        vad_enabled=False,
        segment_emit_ms=0,
        segment_emit_bytes=100,
    )

    partial_events = await session.push_audio(b"\x00\x01" * 10)
    stop_events = await session.handle_control(ClientControlEvent(type="stop"))

    assert partial_events == []
    assert [event.type for event in stop_events] == ["final", "translation", "stats"]
    assert stop_events[0].payload["text"] == "🍺"
    assert stop_events[1].payload["translations"] == {}
    assert translator.calls == []


@pytest.mark.anyio
async def test_close_is_idempotent_after_stop() -> None:
    session = RealtimeSession(
        asr=MockStreamingAsr(),
        translator=MockTranslator(default_targets=["ko", "es"]),
        polisher=None,
        target_languages=["ko", "es"],
        vad_enabled=False,
        segment_emit_ms=0,
        segment_emit_bytes=4,
    )

    await session.push_audio(b"\x00\x01" * 2)
    await session.handle_control(ClientControlEvent(type="stop"))

    assert await session.close() == []


@pytest.mark.anyio
async def test_session_can_continue_after_stop_with_new_turn() -> None:
    session = RealtimeSession(
        asr=SequenceAsr(
            [
                AsrResult(text="안녕하세요", language="ko", is_final=True),
                AsrResult(text="다시 시작합니다", language="ko", is_final=True),
            ]
        ),
        translator=MockTranslator(default_targets=["ko", "es"]),
        polisher=None,
        target_languages=["ko", "es"],
        vad_enabled=False,
        segment_emit_ms=0,
        segment_emit_bytes=100,
    )

    await session.handle_control(ClientControlEvent(type="start", sample_rate=16_000, language="ko"))
    assert await session.push_audio(b"\x00\x01" * 10) == []
    first_stop = await session.handle_control(ClientControlEvent(type="stop"))

    await session.handle_control(ClientControlEvent(type="start", sample_rate=16_000, language="ko"))
    assert await session.push_audio(b"\x00\x01" * 10) == []
    second_stop = await session.handle_control(ClientControlEvent(type="stop"))

    assert [event.type for event in first_stop] == ["final", "translation", "stats"]
    assert first_stop[0].payload["text"] == "안녕하세요"
    assert [event.type for event in second_stop] == ["final", "translation", "stats"]
    assert second_stop[0].payload["text"] == "다시 시작합니다"


@pytest.mark.anyio
async def test_duplicate_partial_text_does_not_retranslate() -> None:
    translator = RecordingTranslator()
    session = RealtimeSession(
        asr=SequenceAsr(
            [
                AsrResult(text="지금 잘 들리나요", language="ko", is_final=False),
                AsrResult(text="지금 잘 들리나요", language="ko", is_final=False),
            ]
        ),
        translator=translator,
        polisher=None,
        target_languages=["ko", "es"],
        vad_enabled=False,
        segment_emit_ms=0,
        segment_emit_bytes=4,
    )

    first_events = await session.push_audio(b"\x00\x01" * 2)
    second_events = await session.push_audio(b"\x00\x01" * 2)

    assert [event.type for event in first_events] == ["partial", "translation"]
    assert second_events == []
    assert len(translator.calls) == 1
    assert translator.calls[0]["mode"] == "realtime"


@pytest.mark.anyio
async def test_session_stabilizes_bad_short_phrase_translation() -> None:
    session = RealtimeSession(
        asr=SequenceAsr([AsrResult(text="안녕하세요", language="ko", is_final=True)]),
        translator=SequenceTranslator([{"ko": "안녕하세요", "es": "Hola, por favor."}]),
        polisher=None,
        target_languages=["ko", "es"],
        vad_enabled=False,
        segment_emit_ms=0,
        segment_emit_bytes=4,
    )

    await session.push_audio(b"\x00\x01" * 2)
    stop_events = await session.handle_control(ClientControlEvent(type="stop"))

    assert [event.type for event in stop_events] == ["final", "translation", "stats"]
    assert stop_events[1].payload["translations"]["es"] == "Hola."


@pytest.mark.anyio
async def test_session_canonicalizes_common_spanish_phrase_before_translation() -> None:
    session = RealtimeSession(
        asr=SequenceAsr([AsrResult(text="como estas?", language="es", is_final=True)]),
        translator=SequenceTranslator([{"es": "como estas?", "ko": "지금과 같이요?"}]),
        polisher=None,
        target_languages=["ko", "es"],
        vad_enabled=False,
        segment_emit_ms=0,
        segment_emit_bytes=4,
    )

    await session.push_audio(b"\x00\x01" * 2)
    stop_events = await session.handle_control(ClientControlEvent(type="stop"))

    assert [event.type for event in stop_events] == ["final", "translation", "stats"]
    assert stop_events[0].payload["text"] == "¿Cómo estás?"
    assert stop_events[1].payload["translations"]["ko"] == "어떻게 지내세요?"


@pytest.mark.anyio
async def test_vad_finalizes_after_trailing_silence() -> None:
    session = RealtimeSession(
        asr=MockStreamingAsr(),
        translator=MockTranslator(default_targets=["ko", "es"]),
        polisher=None,
        target_languages=["ko", "es"],
        vad_enabled=True,
        vad_energy_threshold=0.01,
        vad_silence_ms=150,
        vad_min_speech_ms=100,
        vad_preroll_ms=0,
        utterance_max_ms=3000,
        segment_emit_ms=0,
        segment_emit_bytes=4,
    )

    speech_chunk = (2000).to_bytes(2, "little", signed=True) * 1600
    silence_chunk = (0).to_bytes(2, "little", signed=True) * 1600

    assert await session.push_audio(speech_chunk) == []
    assert await session.push_audio(silence_chunk) == []
    events = await session.push_audio(silence_chunk)

    assert [event.type for event in events] == ["final", "translation"]


@pytest.mark.anyio
async def test_vad_emits_partial_translation_before_final() -> None:
    session = RealtimeSession(
        asr=MockStreamingAsr(),
        translator=MockTranslator(default_targets=["ko", "es"]),
        polisher=None,
        target_languages=["ko", "es"],
        vad_enabled=True,
        vad_energy_threshold=0.01,
        vad_silence_ms=150,
        vad_min_speech_ms=100,
        vad_preroll_ms=0,
        utterance_max_ms=3000,
        segment_emit_ms=600,
        segment_emit_bytes=4,
    )

    speech_chunk = (2000).to_bytes(2, "little", signed=True) * 1600
    silence_chunk = (0).to_bytes(2, "little", signed=True) * 1600

    for _ in range(5):
        assert await session.push_audio(speech_chunk) == []

    partial_events = await session.push_audio(speech_chunk)
    assert [event.type for event in partial_events] == ["partial", "translation"]
    assert partial_events[1].payload["is_final"] is False

    assert await session.push_audio(silence_chunk) == []
    final_events = await session.push_audio(silence_chunk)
    assert [event.type for event in final_events] == ["final", "translation"]
    assert final_events[1].payload["is_final"] is True


@pytest.mark.anyio
async def test_vad_partial_uses_preview_window_but_final_keeps_full_utterance() -> None:
    asr = RecordingChunkAsr()
    session = RealtimeSession(
        asr=asr,
        translator=MockTranslator(default_targets=["ko", "es"]),
        polisher=None,
        target_languages=["ko", "es"],
        vad_enabled=True,
        vad_energy_threshold=0.01,
        vad_silence_ms=150,
        vad_min_speech_ms=100,
        vad_preroll_ms=0,
        utterance_max_ms=3000,
        segment_emit_ms=600,
        segment_emit_bytes=4,
        partial_preview_ms=300,
    )

    speech_chunk = (2000).to_bytes(2, "little", signed=True) * 1600
    silence_chunk = (0).to_bytes(2, "little", signed=True) * 1600

    for _ in range(5):
        assert await session.push_audio(speech_chunk) == []

    partial_events = await session.push_audio(speech_chunk)
    assert [event.type for event in partial_events] == ["partial", "translation"]

    assert await session.push_audio(silence_chunk) == []
    final_events = await session.push_audio(silence_chunk)
    assert [event.type for event in final_events] == ["final", "translation"]

    partial_call = next(call for call in asr.calls if call["is_final"] is False)
    final_call = next(call for call in asr.calls if call["is_final"] is True)

    assert partial_call["bytes"] == 9600
    assert final_call["bytes"] > partial_call["bytes"]


@pytest.mark.anyio
async def test_auto_mode_does_not_lock_language_hint_from_partial_result() -> None:
    asr = HintRecordingAsr()
    session = RealtimeSession(
        asr=asr,
        translator=MockTranslator(default_targets=["ko", "es"]),
        polisher=None,
        target_languages=["ko", "es"],
        vad_enabled=False,
        segment_emit_ms=0,
        segment_emit_bytes=4,
    )

    await session.push_audio(b"\x00\x01" * 2)
    await session.push_audio(b"\x00\x01" * 2)

    assert asr.languages == ["auto", "auto"]


@pytest.mark.anyio
async def test_non_dialogue_final_output_is_dropped() -> None:
    session = RealtimeSession(
        asr=SequenceAsr([AsrResult(text="(inhales)", language="es", is_final=True)]),
        translator=MockTranslator(default_targets=["ko", "es"]),
        polisher=None,
        target_languages=["ko", "es"],
        vad_enabled=False,
        segment_emit_ms=0,
        segment_emit_bytes=100,
    )

    await session.push_audio(b"\x00\x01" * 10)
    stop_events = await session.handle_control(ClientControlEvent(type="stop"))

    assert [event.type for event in stop_events] == ["stats"]


@pytest.mark.anyio
async def test_known_korean_hallucination_final_output_is_dropped() -> None:
    session = RealtimeSession(
        asr=SequenceAsr([AsrResult(text="MBC 뉴스 김성현입니다.", language="ko", is_final=True)]),
        translator=MockTranslator(default_targets=["ko", "es"]),
        polisher=None,
        target_languages=["ko", "es"],
        vad_enabled=False,
        segment_emit_ms=0,
        segment_emit_bytes=100,
    )

    await session.push_audio(b"\x00\x01" * 10)
    stop_events = await session.handle_control(ClientControlEvent(type="stop"))

    assert [event.type for event in stop_events] == ["stats"]


@pytest.mark.anyio
async def test_known_caption_credit_final_output_is_dropped() -> None:
    session = RealtimeSession(
        asr=SequenceAsr([AsrResult(text="한글자막 by 한효정", language="ko", is_final=True)]),
        translator=MockTranslator(default_targets=["ko", "es"]),
        polisher=None,
        target_languages=["ko", "es"],
        vad_enabled=False,
        segment_emit_ms=0,
        segment_emit_bytes=100,
    )

    await session.push_audio(b"\x00\x01" * 10)
    stop_events = await session.handle_control(ClientControlEvent(type="stop"))

    assert [event.type for event in stop_events] == ["stats"]


@pytest.mark.anyio
async def test_known_news_signoff_final_output_is_dropped() -> None:
    session = RealtimeSession(
        asr=SequenceAsr([AsrResult(text="지금까지 뉴스 스토리였습니다.", language="ko", is_final=True)]),
        translator=MockTranslator(default_targets=["ko", "es"]),
        polisher=None,
        target_languages=["ko", "es"],
        vad_enabled=False,
        segment_emit_ms=0,
        segment_emit_bytes=100,
    )

    await session.push_audio(b"\x00\x01" * 10)
    stop_events = await session.handle_control(ClientControlEvent(type="stop"))

    assert [event.type for event in stop_events] == ["stats"]


@pytest.mark.anyio
async def test_broadcast_thanks_signoff_final_output_is_dropped() -> None:
    session = RealtimeSession(
        asr=SequenceAsr([AsrResult(text="시청해주셔서 감사합니다.", language="ko", is_final=True)]),
        translator=MockTranslator(default_targets=["ko", "es"]),
        polisher=None,
        target_languages=["ko", "es"],
        vad_enabled=False,
        segment_emit_ms=0,
        segment_emit_bytes=100,
    )

    await session.push_audio(b"\x00\x01" * 10)
    stop_events = await session.handle_control(ClientControlEvent(type="stop"))

    assert [event.type for event in stop_events] == ["stats"]


@pytest.mark.anyio
async def test_repeated_short_korean_thanks_final_is_dropped_on_second_occurrence() -> None:
    session = RealtimeSession(
        asr=SequenceAsr(
            [
                AsrResult(text="감사합니다.", language="ko", is_final=True),
                AsrResult(text="감사합니다.", language="ko", is_final=True),
            ]
        ),
        translator=MockTranslator(default_targets=["ko", "es"]),
        polisher=None,
        target_languages=["ko", "es"],
        vad_enabled=True,
        vad_energy_threshold=0.01,
        vad_silence_ms=150,
        vad_min_speech_ms=100,
        vad_preroll_ms=0,
        utterance_max_ms=3000,
        segment_emit_ms=6000,
        segment_emit_bytes=999999,
    )

    speech_chunk = (2000).to_bytes(2, "little", signed=True) * 1600
    silence_chunk = (0).to_bytes(2, "little", signed=True) * 1600

    assert await session.push_audio(speech_chunk) == []
    assert await session.push_audio(silence_chunk) == []
    first_final = await session.push_audio(silence_chunk)

    assert [event.type for event in first_final] == ["final", "translation"]
    assert first_final[0].payload["text"] == "감사합니다."

    assert await session.push_audio(speech_chunk) == []
    assert await session.push_audio(silence_chunk) == []
    second_final = await session.push_audio(silence_chunk)

    assert second_final == []


@pytest.mark.anyio
async def test_repeated_short_spanish_thanks_final_is_dropped_on_second_occurrence() -> None:
    session = RealtimeSession(
        asr=SequenceAsr(
            [
                AsrResult(text="Gracias.", language="es", is_final=True),
                AsrResult(text="Muchas gracias.", language="es", is_final=True),
                AsrResult(text="Muchas gracias.", language="es", is_final=True),
            ]
        ),
        translator=MockTranslator(default_targets=["ko", "es"]),
        polisher=None,
        target_languages=["ko", "es"],
        vad_enabled=True,
        vad_energy_threshold=0.01,
        vad_silence_ms=150,
        vad_min_speech_ms=100,
        vad_preroll_ms=0,
        utterance_max_ms=3000,
        segment_emit_ms=6000,
        segment_emit_bytes=999999,
    )

    speech_chunk = (2000).to_bytes(2, "little", signed=True) * 1600
    silence_chunk = (0).to_bytes(2, "little", signed=True) * 1600

    for _index in range(2):
        assert await session.push_audio(speech_chunk) == []
        assert await session.push_audio(silence_chunk) == []
        first_final = await session.push_audio(silence_chunk)
        assert [event.type for event in first_final] == ["final", "translation"]

    assert await session.push_audio(speech_chunk) == []
    assert await session.push_audio(silence_chunk) == []
    third_final = await session.push_audio(silence_chunk)

    assert third_final == []


@pytest.mark.anyio
async def test_common_korean_asr_typos_are_normalized_before_translation() -> None:
    session = RealtimeSession(
        asr=SequenceAsr([AsrResult(text="번역역품들이 너무 낮죠.", language="ko", is_final=True)]),
        translator=MockTranslator(default_targets=["ko", "es"]),
        polisher=None,
        target_languages=["ko", "es"],
        vad_enabled=False,
        segment_emit_ms=0,
        segment_emit_bytes=100,
    )

    await session.push_audio(b"\x00\x01" * 10)
    stop_events = await session.handle_control(ClientControlEvent(type="stop"))

    assert [event.type for event in stop_events] == ["final", "translation", "stats"]
    assert stop_events[0].payload["text"] == "번역 품질이 너무 낮죠."
    assert stop_events[1].payload["translations"]["es"] == "[ko->es] 번역 품질이 너무 낮죠."


@pytest.mark.anyio
async def test_known_korean_term_alias_is_normalized_before_translation() -> None:
    session = RealtimeSession(
        asr=SequenceAsr([AsrResult(text="카르트리 확인해봐", language="ko", is_final=True)]),
        translator=SequenceTranslator(
            [
                {
                    "ko": "카르트리 확인해봐",
                    "es": "carteri revisalo",
                }
            ]
        ),
        polisher=None,
        target_languages=["ko", "es"],
        vad_enabled=False,
        segment_emit_ms=0,
        segment_emit_bytes=100,
    )

    await session.push_audio(b"\x00\x01" * 10)
    stop_events = await session.handle_control(ClientControlEvent(type="stop"))

    assert [event.type for event in stop_events] == ["final", "translation", "stats"]
    assert stop_events[0].payload["text"] == "카르텔 확인해봐"
    assert stop_events[1].payload["translations"]["es"] == "cartel revisalo"


@pytest.mark.anyio
async def test_translation_term_memory_keeps_previous_preferred_term_form() -> None:
    session = RealtimeSession(
        asr=SequenceAsr(
            [
                AsrResult(text="오비스파도 얘기입니다", language="ko", is_final=True),
                AsrResult(text="오비스파도 다시 확인", language="ko", is_final=True),
            ]
        ),
        translator=SequenceTranslator(
            [
                {
                    "ko": "오비스파도 얘기입니다",
                    "es": "obispado y ya",
                },
                {
                    "ko": "오비스파도 다시 확인",
                    "es": "obispados otra vez",
                },
            ]
        ),
        polisher=None,
        target_languages=["ko", "es"],
        vad_enabled=True,
        vad_energy_threshold=0.01,
        vad_silence_ms=150,
        vad_min_speech_ms=100,
        vad_preroll_ms=0,
        utterance_max_ms=3000,
        segment_emit_ms=6000,
        segment_emit_bytes=999999,
    )

    speech_chunk = (2000).to_bytes(2, "little", signed=True) * 1600
    silence_chunk = (0).to_bytes(2, "little", signed=True) * 1600

    assert await session.push_audio(speech_chunk) == []
    assert await session.push_audio(silence_chunk) == []
    first_final = await session.push_audio(silence_chunk)

    assert [event.type for event in first_final] == ["final", "translation"]
    assert first_final[1].payload["translations"]["es"] == "obispado y ya"

    assert await session.push_audio(speech_chunk) == []
    assert await session.push_audio(silence_chunk) == []
    second_final = await session.push_audio(silence_chunk)

    assert [event.type for event in second_final] == ["final", "translation"]
    assert second_final[1].payload["translations"]["es"] == "obispado otra vez"


@pytest.mark.anyio
async def test_spanish_term_alias_is_normalized_in_korean_translation() -> None:
    session = RealtimeSession(
        asr=SequenceAsr([AsrResult(text="cártel confirmado", language="es", is_final=True)]),
        translator=SequenceTranslator(
            [
                {
                    "es": "cártel confirmado",
                    "ko": "카르트리 확인",
                }
            ]
        ),
        polisher=None,
        target_languages=["ko", "es"],
        vad_enabled=False,
        segment_emit_ms=0,
        segment_emit_bytes=100,
    )

    await session.push_audio(b"\x00\x01" * 10)
    stop_events = await session.handle_control(ClientControlEvent(type="stop"))

    assert [event.type for event in stop_events] == ["final", "translation", "stats"]
    assert stop_events[1].payload["translations"]["ko"] == "카르텔 확인"


@pytest.mark.anyio
async def test_short_korean_fragment_is_held_and_merged_with_next_final() -> None:
    session = RealtimeSession(
        asr=SequenceAsr(
            [
                AsrResult(text="왜냐하면...", language="ko", is_final=True),
                AsrResult(text="요즘 못 잤거든요", language="ko", is_final=True),
            ]
        ),
        translator=MockTranslator(default_targets=["ko", "es"]),
        polisher=None,
        target_languages=["ko", "es"],
        vad_enabled=True,
        vad_energy_threshold=0.01,
        vad_silence_ms=150,
        vad_min_speech_ms=100,
        vad_preroll_ms=0,
        utterance_max_ms=3000,
        segment_emit_ms=6000,
        segment_emit_bytes=999999,
    )

    speech_chunk = (2000).to_bytes(2, "little", signed=True) * 1600
    silence_chunk = (0).to_bytes(2, "little", signed=True) * 1600

    assert await session.push_audio(speech_chunk) == []
    assert await session.push_audio(silence_chunk) == []
    first_final = await session.push_audio(silence_chunk)
    assert first_final == []

    assert await session.push_audio(speech_chunk) == []
    assert await session.push_audio(silence_chunk) == []
    second_final = await session.push_audio(silence_chunk)

    assert [event.type for event in second_final] == ["final", "translation"]
    assert second_final[0].payload["text"] == "왜냐하면 요즘 못 잤거든요"
    assert second_final[1].payload["translations"]["es"] == "[ko->es] 왜냐하면 요즘 못 잤거든요"


@pytest.mark.anyio
async def test_korean_suffix_fragment_is_held_and_merged_with_next_final() -> None:
    session = RealtimeSession(
        asr=SequenceAsr(
            [
                AsrResult(text="이제는 내가 말하는 속도와", language="ko", is_final=True),
                AsrResult(text="발음이 중요합니다", language="ko", is_final=True),
            ]
        ),
        translator=MockTranslator(default_targets=["ko", "es"]),
        polisher=None,
        target_languages=["ko", "es"],
        vad_enabled=True,
        vad_energy_threshold=0.01,
        vad_silence_ms=150,
        vad_min_speech_ms=100,
        vad_preroll_ms=0,
        utterance_max_ms=3000,
        segment_emit_ms=6000,
        segment_emit_bytes=999999,
    )

    speech_chunk = (2000).to_bytes(2, "little", signed=True) * 1600
    silence_chunk = (0).to_bytes(2, "little", signed=True) * 1600

    assert await session.push_audio(speech_chunk) == []
    assert await session.push_audio(silence_chunk) == []
    first_final = await session.push_audio(silence_chunk)
    assert first_final == []

    assert await session.push_audio(speech_chunk) == []
    assert await session.push_audio(silence_chunk) == []
    second_final = await session.push_audio(silence_chunk)

    assert [event.type for event in second_final] == ["final", "translation"]
    assert second_final[0].payload["text"] == "이제는 내가 말하는 속도와 발음이 중요합니다"


@pytest.mark.anyio
async def test_standalone_pacific_hallucination_is_dropped() -> None:
    session = RealtimeSession(
        asr=SequenceAsr([AsrResult(text="태평양", language="ko", is_final=True)]),
        translator=MockTranslator(default_targets=["ko", "es"]),
        polisher=None,
        target_languages=["ko", "es"],
        vad_enabled=False,
        segment_emit_ms=0,
        segment_emit_bytes=100,
    )

    await session.push_audio(b"\x00\x01" * 10)
    stop_events = await session.handle_control(ClientControlEvent(type="stop"))

    assert [event.type for event in stop_events] == ["stats"]


@pytest.mark.anyio
async def test_short_spanish_fragment_is_held_and_merged_with_next_final() -> None:
    session = RealtimeSession(
        asr=SequenceAsr(
            [
                AsrResult(text="Porque...", language="es", is_final=True),
                AsrResult(text="no dormi bien", language="es", is_final=True),
            ]
        ),
        translator=MockTranslator(default_targets=["ko", "es"]),
        polisher=None,
        target_languages=["ko", "es"],
        vad_enabled=True,
        vad_energy_threshold=0.01,
        vad_silence_ms=150,
        vad_min_speech_ms=100,
        vad_preroll_ms=0,
        utterance_max_ms=3000,
        segment_emit_ms=6000,
        segment_emit_bytes=999999,
    )

    speech_chunk = (2000).to_bytes(2, "little", signed=True) * 1600
    silence_chunk = (0).to_bytes(2, "little", signed=True) * 1600

    assert await session.push_audio(speech_chunk) == []
    assert await session.push_audio(silence_chunk) == []
    first_final = await session.push_audio(silence_chunk)
    assert first_final == []

    assert await session.push_audio(speech_chunk) == []
    assert await session.push_audio(silence_chunk) == []
    second_final = await session.push_audio(silence_chunk)

    assert [event.type for event in second_final] == ["final", "translation"]
    assert second_final[0].payload["text"] == "Porque no dormi bien"
    assert second_final[1].payload["translations"]["ko"] == "[es->ko] Porque no dormi bien"


@pytest.mark.anyio
async def test_held_fragment_is_flushed_if_speaker_stops_without_followup() -> None:
    session = RealtimeSession(
        asr=SequenceAsr([AsrResult(text="Porque...", language="es", is_final=True)]),
        translator=MockTranslator(default_targets=["ko", "es"]),
        polisher=None,
        target_languages=["ko", "es"],
        vad_enabled=False,
        segment_emit_ms=0,
        segment_emit_bytes=100,
    )

    await session.push_audio(b"\x00\x01" * 10)
    stop_events = await session.handle_control(ClientControlEvent(type="stop"))

    assert [event.type for event in stop_events] == ["final", "translation", "stats"]
    assert stop_events[0].payload["text"] == "Porque..."
    assert stop_events[1].payload["translations"]["ko"] == "[es->ko] Porque..."


@pytest.mark.anyio
async def test_final_translation_is_polished_with_history() -> None:
    polisher = MockPolisher()
    session = RealtimeSession(
        asr=SequenceAsr(
            [
                AsrResult(text="안녕하세요", language="ko", is_final=True),
                AsrResult(text="오늘 회의 시작합시다", language="ko", is_final=True),
            ]
        ),
        translator=MockTranslator(default_targets=["ko", "es"]),
        polisher=polisher,
        target_languages=["ko", "es"],
        vad_enabled=False,
        segment_emit_ms=0,
        segment_emit_bytes=4,
    )

    first_events = await session.push_audio(b"\x00\x01" * 2)
    second_events = await session.push_audio(b"\x00\x01" * 2)

    assert first_events[1].payload["translations"]["es"].startswith("[polished es]")
    assert second_events[1].payload["translations"]["es"].startswith("[polished es]")
    assert len(polisher.calls) == 2
    assert polisher.calls[1]["conversation_history"]


@pytest.mark.anyio
async def test_partial_translation_is_not_polished_when_scope_is_final() -> None:
    polisher = MockPolisher()
    translator = RecordingTranslator()
    session = RealtimeSession(
        asr=SequenceAsr([AsrResult(text="오늘 바로 시작하겠습니다", language="ko", is_final=False)]),
        translator=translator,
        polisher=polisher,
        target_languages=["ko", "es"],
        vad_enabled=False,
        segment_emit_ms=0,
        segment_emit_bytes=4,
    )

    events = await session.push_audio(b"\x00\x01" * 2)

    assert [event.type for event in events] == ["partial", "translation"]
    assert translator.calls
    assert polisher.calls == []


@pytest.mark.anyio
async def test_unstable_korean_partial_emits_source_only() -> None:
    session = RealtimeSession(
        asr=SequenceAsr([AsrResult(text="왜냐하면", language="ko", is_final=False)]),
        translator=MockTranslator(default_targets=["ko", "es"]),
        polisher=None,
        target_languages=["ko", "es"],
        vad_enabled=False,
        segment_emit_ms=0,
        segment_emit_bytes=4,
    )

    events = await session.push_audio(b"\x00\x01" * 2)

    assert [event.type for event in events] == ["partial"]
