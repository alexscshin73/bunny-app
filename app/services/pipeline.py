from functools import lru_cache

from app.config import Settings
from app.services.asr.base import StreamingAsr
from app.services.asr.mock import MockStreamingAsr
from app.services.asr.whisper_cpp import WhisperCppStreamingAsr
from app.services.llm_postedit import (
    FallbackTranslationPolisher,
    HeuristicTranslationPolisher,
    OpenAICompatibleTranslationPolisher,
    TranslationPolisher,
)
from app.services.session import RealtimeSession
from app.services.translate.base import Translator
from app.services.translate.guardrailed import GuardrailedTranslator
from app.services.translate.mock import MockTranslator
from app.services.translate.nllb_ct2 import NllbCTranslate2Translator


def build_asr(settings: Settings) -> StreamingAsr:
    if settings.asr_engine == "whisper_cpp":
        return WhisperCppStreamingAsr(
            binary_path=settings.whisper_cpp_binary,
            model_path=settings.whisper_model_path,
            default_language=settings.whisper_language,
            no_gpu=settings.whisper_cpp_no_gpu,
            use_vad=settings.whisper_cpp_use_vad,
            vad_model_path=settings.whisper_vad_model_path,
            suppress_non_speech=settings.whisper_cpp_suppress_non_speech,
            no_fallback=settings.whisper_cpp_no_fallback,
            threads=settings.whisper_threads,
            processors=settings.whisper_processors,
            partial_beam_size=settings.whisper_partial_beam_size,
            final_beam_size=settings.whisper_final_beam_size,
            no_speech_threshold=settings.whisper_no_speech_threshold,
            logprob_threshold=settings.whisper_logprob_threshold,
            entropy_threshold=settings.whisper_entropy_threshold,
        )
    return MockStreamingAsr()


def build_translator(settings: Settings) -> Translator:
    translator: Translator
    if settings.translation_engine == "nllb_ct2":
        translator = _cached_nllb_translator(
            model_path=settings.translation_model_path,
            tokenizer_path=settings.translation_tokenizer_path,
            device=settings.translation_device,
            compute_type=settings.translation_compute_type,
            inter_threads=settings.translation_inter_threads,
            intra_threads=settings.translation_intra_threads,
            default_targets=tuple(settings.translation_targets),
        )
    else:
        translator = MockTranslator(default_targets=settings.translation_targets)
    return GuardrailedTranslator(translator)


def build_translation_polisher(settings: Settings) -> TranslationPolisher | None:
    if not settings.llm_postedit_enabled:
        return None
    primary = _cached_llm_polisher(
        base_url=settings.llm_postedit_base_url,
        model=settings.llm_postedit_model,
        api_key=settings.llm_postedit_api_key,
        timeout_s=settings.llm_postedit_timeout_s,
    )
    return FallbackTranslationPolisher(primary=primary, fallback=HeuristicTranslationPolisher())


@lru_cache
def _cached_nllb_translator(
    model_path: str | None,
    tokenizer_path: str | None,
    device: str,
    compute_type: str,
    inter_threads: int,
    intra_threads: int,
    default_targets: tuple[str, ...],
) -> NllbCTranslate2Translator:
    return NllbCTranslate2Translator(
        model_path=model_path,
        tokenizer_path=tokenizer_path,
        device=device,
        compute_type=compute_type,
        inter_threads=inter_threads,
        intra_threads=intra_threads,
        default_targets=list(default_targets),
    )


@lru_cache
def _cached_llm_polisher(
    base_url: str | None,
    model: str | None,
    api_key: str | None,
    timeout_s: float,
) -> OpenAICompatibleTranslationPolisher:
    return OpenAICompatibleTranslationPolisher(
        base_url=base_url,
        model=model,
        api_key=api_key,
        timeout_s=timeout_s,
    )


def describe_runtime(settings: Settings) -> dict[str, object]:
    asr = build_asr(settings)
    translator = build_translator(settings)
    polisher = build_translation_polisher(settings)
    return {
        "asr": asr.status().model_dump(),
        "translation": translator.status().model_dump() | {"targets": settings.translation_targets},
        "llm_postedit": (
            polisher.status().model_dump()
            | {
                "enabled": True,
                "scope": settings.llm_postedit_scope,
                "history_turns": settings.llm_postedit_history_turns,
            }
            if polisher
            else {
                "enabled": False,
                "scope": settings.llm_postedit_scope,
                "history_turns": settings.llm_postedit_history_turns,
            }
        ),
        "speech_runtime": {
            "vad_enabled": settings.vad_enabled,
            "vad_energy_threshold": settings.vad_energy_threshold,
            "vad_silence_ms": settings.vad_silence_ms,
            "vad_min_speech_ms": settings.vad_min_speech_ms,
            "vad_preroll_ms": settings.vad_preroll_ms,
            "utterance_max_ms": settings.utterance_max_ms,
            "segment_emit_ms": settings.segment_emit_ms,
            "segment_emit_bytes": settings.segment_emit_bytes,
            "partial_preview_ms": settings.partial_preview_ms,
        },
    }


def build_realtime_session(settings: Settings) -> RealtimeSession:
    return RealtimeSession(
        asr=build_asr(settings),
        translator=build_translator(settings),
        polisher=build_translation_polisher(settings),
        target_languages=settings.translation_targets,
        vad_enabled=settings.vad_enabled,
        vad_energy_threshold=settings.vad_energy_threshold,
        vad_silence_ms=settings.vad_silence_ms,
        vad_min_speech_ms=settings.vad_min_speech_ms,
        vad_preroll_ms=settings.vad_preroll_ms,
        utterance_max_ms=settings.utterance_max_ms,
        segment_emit_ms=settings.segment_emit_ms,
        segment_emit_bytes=settings.segment_emit_bytes,
        partial_preview_ms=settings.partial_preview_ms,
        history_turn_limit=settings.llm_postedit_history_turns,
        postedit_scope=settings.llm_postedit_scope,
    )


async def warm_runtime(settings: Settings) -> None:
    asr = build_asr(settings)
    translator = build_translator(settings)

    try:
        await asr.transcribe_chunk(
            pcm_chunk=b"\x00\x00" * int(16_000 * 0.35),
            sample_rate=16_000,
            language=settings.whisper_language,
            is_final=False,
        )
    except Exception:
        pass

    if settings.translation_engine != "nllb_ct2":
        return

    try:
        await translator.translate_all(
            text="안녕하세요",
            source_language="ko",
            target_languages=settings.translation_targets,
            mode="quality",
        )
    except Exception:
        return
