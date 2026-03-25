from collections import deque
import logging
import re
import time
from typing import Literal

from app.models.events import ClientControlEvent, ServerEvent
from app.services.asr.base import AsrResult, StreamingAsr
from app.services.llm_postedit import TranslationPolisher
from app.services.nonverbal import is_nonverbal_text
from app.services.terminology import enforce_translation_terms
from app.services.terminology import normalize_source_terms
from app.services.translate.base import Translator
from app.services.translation_guardrails import canonicalize_source_text
from app.services.translation_guardrails import stabilize_translations

logger = logging.getLogger("uvicorn.error")

NON_DIALOGUE_MARKERS = {
    "inhales",
    "sighs",
    "knocking on door",
    "thud",
    "música",
    "musica",
    "noise",
    "소음",
    "음악",
}
KNOWN_HALLUCINATION_KEYS = {
    "mbc뉴스김성현입니다",
    "태평양",
    "elpacifico",
}
KNOWN_HALLUCINATION_PATTERNS = (
    re.compile(r"^mbc\s*뉴스.+입니다\.?$", re.IGNORECASE),
    re.compile(r"^지금까지.+뉴스.+였습니다\.?$"),
    re.compile(r"^(한글)?자막\s*by\s+.+$", re.IGNORECASE),
    re.compile(r"^(끝까지\s+)?시청해\s*주셔서\s+(감사|고맙)(합니다|드립니다)\.?$"),
)
LOW_INFORMATION_REPEAT_KEYS = {
    "감사합니다",
    "고맙습니다",
    "gracias",
    "muchasgracias",
}
LOW_INFORMATION_REPEAT_WINDOW_SECONDS = 8.0
KOREAN_FRAGMENT_PREFIXES = (
    "왜냐하면",
    "그래서",
    "그리고",
    "근데",
    "그래도",
    "그러면",
    "자,",
    "자 ",
)
SPANISH_FRAGMENT_PREFIXES = (
    "porque",
    "pero",
    "entonces",
    "y",
    "o sea",
    "a ver",
    "este",
    "pues",
)
FRAGMENT_SUFFIXES = (
    "...",
    "…",
)
KOREAN_HOLD_ENDINGS = (
    "와",
    "과",
    "랑",
    "하고",
    "에서",
    "부터",
    "까지",
    "처럼",
    "때문에",
    "때문",
    "인데",
    "말이",
    "좀",
)
SPANISH_HOLD_ENDINGS = (
    "de",
    "del",
    "y",
    "o",
    "con",
    "para",
    "por",
    "como",
)


class RealtimeSession:
    def __init__(
        self,
        asr: StreamingAsr,
        translator: Translator,
        polisher: TranslationPolisher | None,
        target_languages: list[str],
        vad_enabled: bool = False,
        vad_energy_threshold: float = 0.015,
        vad_silence_ms: int = 700,
        vad_min_speech_ms: int = 400,
        vad_preroll_ms: int = 200,
        utterance_max_ms: int = 6000,
        segment_emit_ms: int = 2000,
        segment_emit_bytes: int = 32_000,
        partial_preview_ms: int = 2200,
        history_turn_limit: int = 4,
        postedit_scope: Literal["final", "all"] = "final",
    ) -> None:
        self.asr = asr
        self.translator = translator
        self.polisher = polisher
        self.target_languages = target_languages
        self.vad_enabled = vad_enabled
        self.vad_energy_threshold = vad_energy_threshold
        self.vad_silence_ms = vad_silence_ms
        self.vad_min_speech_ms = vad_min_speech_ms
        self.vad_preroll_ms = vad_preroll_ms
        self.utterance_max_ms = utterance_max_ms
        self.segment_emit_ms = segment_emit_ms
        self.segment_emit_bytes = segment_emit_bytes
        self.partial_preview_ms = partial_preview_ms
        self.postedit_scope = postedit_scope
        self.sample_rate = 16_000
        self.language = "auto"
        self.audio_buffer = bytearray()
        self.preroll_chunks: deque[bytes] = deque()
        self.preroll_bytes = 0
        self.in_speech = False
        self.trailing_silence_ms = 0.0
        self.utterance_duration_ms = 0.0
        self.total_audio_bytes = 0
        self.last_result: AsrResult | None = None
        self.last_partial_emitted_at_ms = 0.0
        self.last_partial_text = ""
        self.utterance_language_hint: str | None = None
        self.pending_final_fragment: AsrResult | None = None
        self.last_low_information_final_key = ""
        self.last_low_information_final_at = 0.0
        self.conversation_history: deque[dict[str, object]] = deque(maxlen=max(history_turn_limit, 1))
        self.stopped_cleanly = False
        self.terminated = False

    async def handle_control(self, control: ClientControlEvent) -> list[ServerEvent]:
        if control.type == "start":
            if control.sample_rate:
                self.sample_rate = control.sample_rate
            if control.language:
                self.language = control.language
            self.stopped_cleanly = False
            return [
                ServerEvent(
                    type="session_started",
                    payload={"sample_rate": self.sample_rate, "language": self.language},
                )
            ]

        if control.type == "ping":
            return [ServerEvent(type="stats", payload=self._stats_payload())]

        if control.type == "stop":
            if self.terminated:
                return []
            events = await self.flush(is_final=True)
            self.stopped_cleanly = True
            return events

        return []

    async def push_audio(self, chunk: bytes) -> list[ServerEvent]:
        if self.terminated:
            return []
        if chunk:
            self.stopped_cleanly = False

        if self.vad_enabled:
            return await self._push_audio_vad(chunk)

        self.audio_buffer.extend(chunk)
        self.total_audio_bytes += len(chunk)

        if len(self.audio_buffer) < self._emit_threshold_bytes():
            return []

        buffered = bytes(self.audio_buffer)
        self.audio_buffer.clear()
        return await self._transcribe_and_translate(buffered, is_final=False)

    async def flush(self, is_final: bool) -> list[ServerEvent]:
        if self.vad_enabled:
            return await self._flush_vad(is_final=is_final)

        if not self.audio_buffer:
            if is_final:
                pending_events = await self._emit_pending_fragment()
                if pending_events:
                    pending_events.append(ServerEvent(type="stats", payload=self._stats_payload()))
                    return pending_events
                return await self._finalize_without_buffer()
            return []

        buffered = bytes(self.audio_buffer)
        self.audio_buffer.clear()
        events = await self._transcribe_and_translate(buffered, is_final=is_final)
        if is_final:
            if not events:
                events = await self._emit_pending_fragment()
            events.append(ServerEvent(type="stats", payload=self._stats_payload()))
        return events

    async def close(self) -> list[ServerEvent]:
        if self.terminated:
            return []
        self.terminated = True
        if self.stopped_cleanly and not self.audio_buffer and not self.pending_final_fragment:
            if not self.last_result or self.last_result.is_final:
                return []
        return await self.flush(is_final=True)

    async def _transcribe_and_translate(self, pcm_chunk: bytes, is_final: bool) -> list[ServerEvent]:
        audio_seconds = len(pcm_chunk) / max(self.sample_rate * 2, 1)
        pipeline_started = time.perf_counter()
        asr_started = pipeline_started
        result = await self.asr.transcribe_chunk(
            pcm_chunk=pcm_chunk,
            sample_rate=self.sample_rate,
            language=self._requested_language(),
            is_final=is_final,
        )
        asr_elapsed_ms = round((time.perf_counter() - asr_started) * 1000, 1)
        result = self._normalize_asr_result(result)

        if not result.text.strip():
            return []

        result = self._merge_pending_fragment(result)
        if not result.text.strip():
            return []

        if self._should_hold_final_fragment(result):
            self.pending_final_fragment = result
            self.last_result = result
            logger.info(
                "session hold-final-fragment lang=%s text=%r",
                result.language,
                result.text[:120],
            )
            return []

        if not result.is_final and result.text.strip() == self.last_partial_text:
            return []

        self.last_result = result
        self._update_utterance_language_hint(result)
        events = await self._translate_result(
            result=result,
            audio_seconds=round(audio_seconds, 2),
            asr_elapsed_ms=asr_elapsed_ms,
            pipeline_started=pipeline_started,
        )
        if events and not result.is_final:
            self.last_partial_text = result.text.strip()
        return events

    def _asr_event(self, result: AsrResult, metrics: dict[str, float] | None = None) -> ServerEvent:
        event_type = "final" if result.is_final else "partial"
        return ServerEvent(
            type=event_type,
            payload={
                "text": result.text,
                "language": result.language,
                "metrics": metrics or {},
            },
        )

    async def _finalize_without_buffer(self) -> list[ServerEvent]:
        events: list[ServerEvent] = []
        if self.last_result and not self.last_result.is_final:
            final_result = AsrResult(
                text=self.last_result.text,
                language=self.last_result.language,
                is_final=True,
            )
            self.last_result = final_result
            translated_events = await self._translate_result(
                result=final_result,
                audio_seconds=0.0,
                asr_elapsed_ms=0.0,
                pipeline_started=time.perf_counter(),
            )
            events.extend(translated_events)

        events.append(ServerEvent(type="stats", payload=self._stats_payload()))
        return events

    def _stats_payload(self) -> dict[str, int]:
        return {
            "total_audio_bytes": self.total_audio_bytes,
            "buffered_audio_bytes": len(self.audio_buffer),
            "in_speech": self.in_speech,
            "utterance_duration_ms": round(self.utterance_duration_ms, 1),
            "emit_threshold_bytes": self._emit_threshold_bytes(),
            "emit_threshold_seconds": round(self._emit_threshold_bytes() / max(self.sample_rate * 2, 1), 2),
        }

    def _emit_threshold_bytes(self) -> int:
        duration_bytes = int(self.sample_rate * 2 * (self.segment_emit_ms / 1000))
        return max(self.segment_emit_bytes, duration_bytes)

    async def _push_audio_vad(self, chunk: bytes) -> list[ServerEvent]:
        self.total_audio_bytes += len(chunk)

        chunk_duration_ms = self._chunk_duration_ms(chunk)
        chunk_energy = self._chunk_energy(chunk)
        is_speech = chunk_energy >= self.vad_energy_threshold

        if self.in_speech:
            self.audio_buffer.extend(chunk)
            self.utterance_duration_ms += chunk_duration_ms

            if is_speech:
                self.trailing_silence_ms = 0.0
            else:
                self.trailing_silence_ms += chunk_duration_ms

            if self.trailing_silence_ms >= self.vad_silence_ms:
                return await self._finalize_vad_segment()
            if self.utterance_duration_ms >= self.utterance_max_ms:
                return await self._finalize_vad_segment()
            return await self._maybe_emit_partial_vad()

        if not is_speech:
            self._append_preroll(chunk)
            return []

        self.in_speech = True
        self.trailing_silence_ms = 0.0
        self.audio_buffer.extend(self._consume_preroll())
        self.audio_buffer.extend(chunk)
        self.utterance_duration_ms = self._chunk_duration_ms(bytes(self.audio_buffer))

        if self.utterance_duration_ms >= self.utterance_max_ms:
            return await self._finalize_vad_segment()
        return await self._maybe_emit_partial_vad()

    async def _flush_vad(self, is_final: bool) -> list[ServerEvent]:
        if not self.audio_buffer:
            if is_final:
                pending_events = await self._emit_pending_fragment()
                if pending_events:
                    pending_events.append(ServerEvent(type="stats", payload=self._stats_payload()))
                    return pending_events
                return await self._finalize_without_buffer()
            return []

        buffered = bytes(self.audio_buffer)
        self._reset_utterance_state()
        events = await self._transcribe_and_translate(buffered, is_final=True)
        if is_final:
            if not events:
                events = await self._emit_pending_fragment()
            events.append(ServerEvent(type="stats", payload=self._stats_payload()))
        return events

    async def _finalize_vad_segment(self) -> list[ServerEvent]:
        if self.utterance_duration_ms < self.vad_min_speech_ms:
            self._reset_utterance_state()
            return []

        buffered = bytes(self.audio_buffer)
        self._reset_utterance_state()
        return await self._transcribe_and_translate(buffered, is_final=True)

    async def _maybe_emit_partial_vad(self) -> list[ServerEvent]:
        if not self.audio_buffer:
            return []

        emit_interval_ms = max(self.segment_emit_ms, 400)
        if self.utterance_duration_ms < emit_interval_ms:
            return []

        if (self.utterance_duration_ms - self.last_partial_emitted_at_ms) < emit_interval_ms:
            return []

        events = await self._transcribe_and_translate(self._partial_preview_pcm_chunk(), is_final=False)
        self.last_partial_emitted_at_ms = self.utterance_duration_ms
        return events

    def _append_preroll(self, chunk: bytes) -> None:
        self.preroll_chunks.append(chunk)
        self.preroll_bytes += len(chunk)

        while self.preroll_bytes > self._preroll_max_bytes():
            removed = self.preroll_chunks.popleft()
            self.preroll_bytes -= len(removed)

    def _consume_preroll(self) -> bytes:
        preroll = b"".join(self.preroll_chunks)
        self.preroll_chunks.clear()
        self.preroll_bytes = 0
        return preroll

    def _reset_utterance_state(self) -> None:
        self.audio_buffer.clear()
        self.in_speech = False
        self.trailing_silence_ms = 0.0
        self.utterance_duration_ms = 0.0
        self.last_partial_emitted_at_ms = 0.0
        self.last_partial_text = ""
        self.utterance_language_hint = None

    def _chunk_duration_ms(self, chunk: bytes) -> float:
        return len(chunk) / max(self.sample_rate * 2, 1) * 1000

    def _chunk_energy(self, chunk: bytes) -> float:
        usable_length = len(chunk) - (len(chunk) % 2)
        if usable_length <= 0:
            return 0.0

        samples = memoryview(chunk[:usable_length]).cast("h")
        if not samples:
            return 0.0

        total = 0
        for sample in samples:
            total += abs(sample)
        return total / len(samples) / 32768

    def _preroll_max_bytes(self) -> int:
        return int(self.sample_rate * 2 * (self.vad_preroll_ms / 1000))

    def _partial_preview_pcm_chunk(self) -> bytes:
        buffered = bytes(self.audio_buffer)
        if self.partial_preview_ms <= 0:
            return buffered

        preview_bytes = int(self.sample_rate * 2 * (self.partial_preview_ms / 1000))
        if preview_bytes <= 0 or len(buffered) <= preview_bytes:
            return buffered
        return buffered[-preview_bytes:]

    def _requested_language(self) -> str:
        if self.language != "auto":
            return self.language
        if self.utterance_language_hint in self.target_languages:
            return self.utterance_language_hint
        return self.language

    def _update_utterance_language_hint(self, result: AsrResult) -> None:
        if self.language != "auto":
            return
        if not result.is_final:
            return
        if result.language in self.target_languages:
            self.utterance_language_hint = result.language

    async def _emit_pending_fragment(self) -> list[ServerEvent]:
        if not self.pending_final_fragment:
            return []

        result = self.pending_final_fragment
        self.pending_final_fragment = None
        return await self._translate_result(
            result=result,
            audio_seconds=0.0,
            asr_elapsed_ms=0.0,
            pipeline_started=time.perf_counter(),
        )

    async def _translate_result(
        self,
        result: AsrResult,
        audio_seconds: float,
        asr_elapsed_ms: float,
        pipeline_started: float,
    ) -> list[ServerEvent]:
        translation_started = time.perf_counter()
        if is_nonverbal_text(result.text):
            translation_elapsed_ms = round((time.perf_counter() - translation_started) * 1000, 1)
            pipeline_elapsed_ms = round((time.perf_counter() - pipeline_started) * 1000, 1)
            metrics = {
                "audio_seconds": audio_seconds,
                "asr_ms": asr_elapsed_ms,
                "translation_ms": translation_elapsed_ms,
                "pipeline_ms": pipeline_elapsed_ms,
            }
            logger.info(
                "session %s-nonverbal lang=%s audio=%.2fs asr=%.1fms pipeline=%.1fms text=%r",
                "final" if result.is_final else "partial",
                result.language,
                audio_seconds,
                asr_elapsed_ms,
                pipeline_elapsed_ms,
                result.text[:120],
            )
            if result.is_final:
                self._remember_final_turn(result, {})
            return [
                self._asr_event(result, metrics),
                ServerEvent(
                    type="translation",
                    payload={
                        "is_final": result.is_final,
                        "source_language": result.language,
                        "source_text": result.text,
                        "translations": {},
                        "metrics": metrics,
                    },
                ),
            ]

        if not result.is_final and not self._should_translate_partial(result):
            translation_elapsed_ms = round((time.perf_counter() - translation_started) * 1000, 1)
            pipeline_elapsed_ms = round((time.perf_counter() - pipeline_started) * 1000, 1)
            metrics = {
                "audio_seconds": audio_seconds,
                "asr_ms": asr_elapsed_ms,
                "translation_ms": translation_elapsed_ms,
                "pipeline_ms": pipeline_elapsed_ms,
            }
            logger.info(
                "session partial-source-only lang=%s audio=%.2fs asr=%.1fms pipeline=%.1fms text=%r",
                result.language,
                audio_seconds,
                asr_elapsed_ms,
                pipeline_elapsed_ms,
                result.text[:120],
            )
            return [self._asr_event(result, metrics)]

        translations = await self.translator.translate_all(
            text=result.text,
            source_language=result.language,
            target_languages=self.target_languages,
            mode="quality" if result.is_final else "realtime",
        )
        translations = stabilize_translations(
            source_text=result.text,
            source_language=result.language,
            translations=translations,
        )
        translations = self._apply_translation_terminology(result, translations)
        if result.is_final or self.postedit_scope == "all":
            translations = await self._polish_final_translations(result, translations)
            translations = stabilize_translations(
                source_text=result.text,
                source_language=result.language,
                translations=translations,
            )
            translations = self._apply_translation_terminology(result, translations)
        translation_elapsed_ms = round((time.perf_counter() - translation_started) * 1000, 1)
        pipeline_elapsed_ms = round((time.perf_counter() - pipeline_started) * 1000, 1)
        metrics = {
            "audio_seconds": audio_seconds,
            "asr_ms": asr_elapsed_ms,
            "translation_ms": translation_elapsed_ms,
            "pipeline_ms": pipeline_elapsed_ms,
        }
        logger.info(
            "session %s lang=%s audio=%.2fs asr=%.1fms translation=%.1fms pipeline=%.1fms text=%r",
            "final" if result.is_final else "partial",
            result.language,
            audio_seconds,
            asr_elapsed_ms,
            translation_elapsed_ms,
            pipeline_elapsed_ms,
            result.text[:120],
        )
        if result.is_final:
            self._remember_final_turn(result, translations)

        return [
            self._asr_event(result, metrics),
            ServerEvent(
                type="translation",
                payload={
                    "is_final": result.is_final,
                    "source_language": result.language,
                    "source_text": result.text,
                    "translations": translations,
                    "metrics": metrics,
                },
            ),
        ]

    async def _polish_final_translations(
        self,
        result: AsrResult,
        translations: dict[str, str],
    ) -> dict[str, str]:
        if not self.polisher:
            return translations

        polished = dict(translations)
        for target_language, draft in translations.items():
            if target_language == result.language or not draft.strip():
                continue
            try:
                polished[target_language] = await self.polisher.polish_translation(
                    source_text=result.text,
                    source_language=result.language,
                    target_language=target_language,
                    draft_translation=draft,
                    conversation_history=list(self.conversation_history),
                )
            except Exception:
                logger.exception("llm postedit failed for target=%s", target_language)
                polished[target_language] = draft
        return polished

    def _remember_final_turn(self, result: AsrResult, translations: dict[str, str]) -> None:
        self.conversation_history.append(
            {
                "source_language": result.language,
                "source_text": result.text,
                "translations": dict(translations),
            }
        )

    def _should_translate_partial(self, result: AsrResult) -> bool:
        text = result.text.strip()
        if not text:
            return False

        if result.language == "ko":
            normalized = text.rstrip(".!?~ ")
            if any(normalized.startswith(prefix) for prefix in KOREAN_FRAGMENT_PREFIXES):
                return False
            return len(normalized) >= 8

        if result.language == "es":
            words = [word for word in re.split(r"\s+", text.strip(" .!?")) if word]
            return len(words) >= 3

        return len(text) >= 8

    def _normalize_asr_result(self, result: AsrResult) -> AsrResult:
        text = result.text.strip()
        if not text:
            return result
        if _is_non_dialogue_text(text):
            return AsrResult(text="", language=result.language, is_final=result.is_final)
        if result.language == "ko":
            text = _normalize_korean_asr_text(text)
        text = normalize_source_terms(text, result.language)
        text = canonicalize_source_text(text, language=result.language)
        if result.is_final and self._should_drop_repeated_low_information_final(text):
            logger.info(
                "session drop-repeated-short-final lang=%s text=%r",
                result.language,
                text[:120],
            )
            return AsrResult(text="", language=result.language, is_final=True)
        return AsrResult(text=text, language=result.language, is_final=result.is_final)

    def _should_drop_repeated_low_information_final(self, text: str) -> bool:
        key = _normalize_hallucination_key(text)
        if key not in LOW_INFORMATION_REPEAT_KEYS:
            self.last_low_information_final_key = ""
            self.last_low_information_final_at = 0.0
            return False

        now = time.monotonic()
        should_drop = (
            key == self.last_low_information_final_key
            and (now - self.last_low_information_final_at) <= LOW_INFORMATION_REPEAT_WINDOW_SECONDS
        )
        self.last_low_information_final_key = key
        self.last_low_information_final_at = now
        return should_drop

    def _apply_translation_terminology(
        self,
        result: AsrResult,
        translations: dict[str, str],
    ) -> dict[str, str]:
        normalized = dict(translations)
        for target_language, translation_text in translations.items():
            if target_language == result.language or not translation_text.strip():
                continue
            normalized[target_language] = enforce_translation_terms(
                source_text=result.text,
                source_language=result.language,
                target_language=target_language,
                translation_text=translation_text,
                conversation_history=list(self.conversation_history),
            )
        return normalized

    def _merge_pending_fragment(self, result: AsrResult) -> AsrResult:
        if not self.pending_final_fragment or not result.is_final:
            return result

        pending = self.pending_final_fragment
        self.pending_final_fragment = None

        if pending.language != result.language:
            return result

        return AsrResult(
            text=_merge_fragment_text(pending.text, result.text),
            language=result.language,
            is_final=True,
        )

    def _should_hold_final_fragment(self, result: AsrResult) -> bool:
        if not result.is_final:
            return False

        text = result.text.strip()
        if not text:
            return False
        if any(text.endswith(suffix) for suffix in FRAGMENT_SUFFIXES):
            return True

        normalized = text.rstrip(".!?~ ").strip()
        if result.language == "ko":
            if normalized.startswith(KOREAN_FRAGMENT_PREFIXES):
                return True
            return _has_korean_incomplete_suffix(normalized)

        if result.language == "es":
            lowered = normalized.casefold()
            word_count = len([word for word in re.split(r"\s+", lowered) if word])
            if lowered.startswith(SPANISH_FRAGMENT_PREFIXES):
                return True
            if word_count > 0 and word_count <= 5 and _has_spanish_incomplete_suffix(lowered):
                return True
            return False

        return False


def _is_non_dialogue_text(text: str) -> bool:
    stripped = text.strip()
    normalized = stripped.strip("[]()").strip().casefold()
    if normalized in NON_DIALOGUE_MARKERS:
        return True
    if _normalize_hallucination_key(stripped) in KNOWN_HALLUCINATION_KEYS:
        return True
    if any(pattern.fullmatch(stripped) for pattern in KNOWN_HALLUCINATION_PATTERNS):
        return True

    if len(stripped) >= 2 and ((stripped[0], stripped[-1]) in {("(", ")"), ("[", "]")}):
        inner = stripped[1:-1].strip()
        inner_normalized = inner.casefold()
        if inner_normalized in NON_DIALOGUE_MARKERS:
            return True
        if re.fullmatch(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ\s'!?.-]+", inner):
            return True
        if re.fullmatch(r"[가-힣\s]+", inner):
            return True

    return False


def _normalize_hallucination_key(text: str) -> str:
    return re.sub(r"[^0-9A-Za-zÁÉÍÓÚÜÑáéíóúüñ가-힣]+", "", text).casefold()


def _normalize_korean_asr_text(text: str) -> str:
    normalized = text
    normalized = re.sub(r"잘\s+떨리(나|나요|니)", r"잘 들리\1", normalized)
    normalized = normalized.replace("뭔 없어요", "뭐 없어요")
    normalized = normalized.replace("-뭔", "-뭐")
    normalized = normalized.replace("번역역품들이", "번역 품질이")
    normalized = normalized.replace("번역역품이", "번역 품질이")
    normalized = normalized.replace("번역역품들", "번역 품질")
    normalized = normalized.replace("번역역품", "번역 품질")
    normalized = normalized.replace("품빌", "품질")
    normalized = normalized.replace("품질이 너무 낫군요", "품질이 너무 낮군요")
    normalized = normalized.replace("품질이 너무 낫죠", "품질이 너무 낮죠")
    normalized = re.sub(r"\s+", " ", normalized).strip()
    return normalized


def _has_korean_incomplete_suffix(text: str) -> bool:
    if not text:
        return False
    last_token = text.split()[-1]
    if len(last_token) <= 1:
        return False
    return any(last_token.endswith(ending) for ending in KOREAN_HOLD_ENDINGS)


def _has_spanish_incomplete_suffix(text: str) -> bool:
    if not text:
        return False
    last_token = text.split()[-1].strip(".,!?;:")
    if len(last_token) <= 1:
        return False
    return last_token in SPANISH_HOLD_ENDINGS


def _merge_fragment_text(left: str, right: str) -> str:
    merged_left = left.rstrip(".!?~ ").rstrip(".").rstrip("…").rstrip()
    merged_right = right.lstrip("- ").strip()
    if not merged_left:
        return merged_right
    if not merged_right:
        return merged_left
    return f"{merged_left} {merged_right}".strip()
