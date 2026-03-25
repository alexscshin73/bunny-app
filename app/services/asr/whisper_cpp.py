import asyncio
import re
import shutil
from pathlib import Path
from tempfile import TemporaryDirectory

from app.services.asr.base import AsrBackendStatus, AsrResult, StreamingAsr
from app.services.audio import pcm16le_to_wav_bytes

KO_ES_AUTO_LANGUAGES = ("ko", "es")
SPANISH_TEXT_MARKERS = (" que ", " de ", " el ", " la ", " y ", " en ", " muy ", " bien ")
SPANISH_STOPWORDS = {
    "a", "al", "como", "con", "de", "del", "el", "ella", "en", "es", "esta", "este",
    "estos", "haz", "la", "las", "lo", "los", "más", "muy", "número", "para", "pero",
    "por", "qué", "que", "quieres", "si", "sus", "te", "ti", "tienes", "trabajo", "tu",
    "una", "uno", "un", "y",
}
KOREAN_PARTICLE_ENDINGS = (
    "은", "는", "이", "가", "을", "를", "에", "에서", "에게", "으로", "로", "도", "만", "요",
    "다", "니다", "습니다", "거든요", "네요", "죠", "고", "며",
)
KOREAN_COMMON_WORDS = {
    "근데", "그리고", "그게", "뭐냐", "뭐냐면", "왜냐하면", "이게", "이란", "북한", "중요한",
    "가능성", "무시해서는", "얻었거든요", "탄도미사일", "두", "번째는",
}
KNOWN_HALLUCINATION_KEYS = {
    "mbc뉴스김성현입니다",
}


class WhisperCppStreamingAsr(StreamingAsr):
    def __init__(
        self,
        binary_path: str | None,
        model_path: str | None,
        default_language: str = "auto",
        no_gpu: bool = True,
        use_vad: bool = False,
        vad_model_path: str | None = None,
        suppress_non_speech: bool = True,
        no_fallback: bool = True,
        threads: int = 4,
        processors: int = 1,
        partial_beam_size: int = 2,
        final_beam_size: int = 5,
        no_speech_threshold: float = 0.8,
        logprob_threshold: float = -0.5,
        entropy_threshold: float = 2.2,
    ) -> None:
        self.binary_path = binary_path
        self.model_path = model_path
        self.default_language = default_language
        self.no_gpu = no_gpu
        self.use_vad = use_vad
        self.vad_model_path = vad_model_path
        self.suppress_non_speech = suppress_non_speech
        self.no_fallback = no_fallback
        self.threads = max(threads, 1)
        self.processors = max(processors, 1)
        self.partial_beam_size = max(partial_beam_size, 1)
        self.final_beam_size = max(final_beam_size, 1)
        self.no_speech_threshold = no_speech_threshold
        self.logprob_threshold = logprob_threshold
        self.entropy_threshold = entropy_threshold

    def status(self) -> AsrBackendStatus:
        resolved_binary = self._resolve_binary_path()
        resolved_model = self._resolve_model_path()
        model_exists = bool(resolved_model and resolved_model.exists())

        return AsrBackendStatus(
            engine="whisper_cpp",
            ready=bool(resolved_binary and model_exists),
            details={
                "binary_path": str(resolved_binary) if resolved_binary else None,
                "binary_found": bool(resolved_binary),
                "model_path": str(resolved_model) if resolved_model else None,
                "model_found": model_exists,
                "default_language": self.default_language,
                "restricted_auto_languages": ",".join(KO_ES_AUTO_LANGUAGES),
                "no_gpu": self.no_gpu,
                "use_vad": self.use_vad,
                "vad_model_path": str(self._resolve_vad_model_path()) if self._resolve_vad_model_path() else None,
                "suppress_non_speech": self.suppress_non_speech,
                "no_fallback": self.no_fallback,
                "threads": self.threads,
                "processors": self.processors,
                "partial_beam_size": self.partial_beam_size,
                "final_beam_size": self.final_beam_size,
                "no_speech_threshold": self.no_speech_threshold,
                "logprob_threshold": self.logprob_threshold,
                "entropy_threshold": self.entropy_threshold,
            },
        )

    async def transcribe_chunk(
        self,
        pcm_chunk: bytes,
        sample_rate: int,
        language: str,
        is_final: bool,
    ) -> AsrResult:
        binary_path = self._require_binary_path()
        model_path = self._require_model_path()
        candidate_languages = self._candidate_languages(language)
        auto_requested = language.strip().lower() == "auto"

        with TemporaryDirectory(prefix="bunny-app-whisper-") as tmp_dir:
            tmp_path = Path(tmp_dir)
            wav_path = tmp_path / "chunk.wav"
            wav_path.write_bytes(pcm16le_to_wav_bytes(pcm_chunk, sample_rate))

            if auto_requested and len(candidate_languages) > 1:
                transcript = await self._transcribe_wav(
                    binary_path=binary_path,
                    model_path=model_path,
                    wav_path=wav_path,
                    out_prefix=tmp_path / "chunk-auto",
                    language="auto",
                    is_final=is_final,
                )
                normalized = transcript.strip()
                if should_retry_restricted_auto(normalized):
                    transcripts: dict[str, str] = {}
                    for candidate_language in candidate_languages:
                        candidate_transcript = await self._transcribe_wav(
                            binary_path=binary_path,
                            model_path=model_path,
                            wav_path=wav_path,
                            out_prefix=tmp_path / f"chunk-{candidate_language}",
                            language=candidate_language,
                            is_final=is_final,
                        )
                        transcripts[candidate_language] = candidate_transcript

                    effective_language, text = select_best_ko_es_result(transcripts)
                    return AsrResult(
                        text=text,
                        language=effective_language if effective_language else "unknown",
                        is_final=is_final,
                    )

                effective_language = infer_best_ko_es_language(normalized)
                return AsrResult(
                    text=normalized,
                    language=effective_language if normalized else "unknown",
                    is_final=is_final,
                )

            transcripts: dict[str, str] = {}
            for candidate_language in candidate_languages:
                transcript = await self._transcribe_wav(
                    binary_path=binary_path,
                    model_path=model_path,
                    wav_path=wav_path,
                    out_prefix=tmp_path / f"chunk-{candidate_language}",
                    language=candidate_language,
                    is_final=is_final,
                )
                transcripts[candidate_language] = transcript

        effective_language, text = select_best_ko_es_result(transcripts)

        return AsrResult(
            text=text,
            language=effective_language if effective_language else "unknown",
            is_final=is_final,
        )

    async def _detect_language(
        self,
        binary_path: Path,
        model_path: Path,
        pcm_chunk: bytes,
        sample_rate: int,
    ) -> tuple[str, float]:
        with TemporaryDirectory(prefix="bunny-app-whisper-detect-") as tmp_dir:
            tmp_path = Path(tmp_dir)
            wav_path = tmp_path / "detect.wav"
            wav_path.write_bytes(pcm16le_to_wav_bytes(pcm_chunk, sample_rate))

            process = await asyncio.create_subprocess_exec(
                str(binary_path),
                "-m",
                str(model_path),
                "-f",
                str(wav_path),
                "-dl",
                *(["-ng"] if self.no_gpu else []),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, stderr = await process.communicate()

        if process.returncode != 0:
            return "", 0.0

        detect_output = "\n".join(
            part.decode("utf-8", errors="ignore") for part in (stdout, stderr) if part
        )
        return parse_detected_language_output(detect_output)

    async def _transcribe_wav(
        self,
        binary_path: Path,
        model_path: Path,
        wav_path: Path,
        out_prefix: Path,
        language: str,
        is_final: bool,
    ) -> str:
        process = await asyncio.create_subprocess_exec(
            *self._transcribe_command(
                binary_path=binary_path,
                model_path=model_path,
                wav_path=wav_path,
                out_prefix=out_prefix,
                language=language,
                is_final=is_final,
            ),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        _, stderr = await process.communicate()

        if process.returncode != 0:
            error_text = stderr.decode("utf-8", errors="ignore").strip()
            raise RuntimeError(f"whisper.cpp failed: {error_text}")

        transcript_path = out_prefix.with_suffix(".txt")
        text = transcript_path.read_text(encoding="utf-8").strip()
        if text == "[BLANK_AUDIO]":
            return ""
        return text

    def _transcribe_command(
        self,
        binary_path: Path,
        model_path: Path,
        wav_path: Path,
        out_prefix: Path,
        language: str,
        is_final: bool,
    ) -> list[str]:
        return [
            str(binary_path),
            "-m",
            str(model_path),
            "-f",
            str(wav_path),
            "-of",
            str(out_prefix),
            "-otxt",
            "-np",
            "-t",
            str(self.threads),
            "-p",
            str(self.processors),
            "-bs",
            str(self._beam_size_for(is_final)),
            *(["-ng"] if self.no_gpu else []),
            *(["-sns"] if self.suppress_non_speech else []),
            *(["-nf"] if self.no_fallback else []),
            "-nth",
            str(self.no_speech_threshold),
            "-lpt",
            str(self.logprob_threshold),
            "-et",
            str(self.entropy_threshold),
            *(self._vad_args()),
            *(["-l", language] if language else []),
        ]

    def _candidate_languages(self, requested_language: str) -> tuple[str, ...]:
        normalized = requested_language.strip().lower() if requested_language else ""
        if normalized in KO_ES_AUTO_LANGUAGES:
            return (normalized,)

        default_normalized = self.default_language.strip().lower() if self.default_language else ""
        if default_normalized in KO_ES_AUTO_LANGUAGES:
            return (default_normalized,)

        return KO_ES_AUTO_LANGUAGES

    def _resolve_binary_path(self) -> Path | None:
        if self.binary_path:
            candidate = Path(self.binary_path).expanduser()
            return candidate if candidate.exists() else None

        discovered = shutil.which("whisper-cli")
        return Path(discovered) if discovered else None

    def _resolve_model_path(self) -> Path | None:
        if not self.model_path:
            return None
        return Path(self.model_path).expanduser()

    def _require_binary_path(self) -> Path:
        binary_path = self._resolve_binary_path()
        if binary_path:
            return binary_path
        raise RuntimeError(
            "whisper.cpp binary not found. Set BUNNY_WHISPER_CPP_BINARY or install whisper-cli in PATH."
        )

    def _require_model_path(self) -> Path:
        model_path = self._resolve_model_path()
        if model_path and model_path.exists():
            return model_path
        raise RuntimeError(
            "whisper.cpp model not found. Set BUNNY_WHISPER_MODEL_PATH to a valid ggml/gguf model file."
        )

    def _resolve_vad_model_path(self) -> Path | None:
        if not self.vad_model_path:
            return None
        candidate = Path(self.vad_model_path).expanduser()
        return candidate if candidate.exists() else None

    def _vad_args(self) -> list[str]:
        if not self.use_vad:
            return []
        vad_model_path = self._resolve_vad_model_path()
        if not vad_model_path:
            return []
        return ["--vad", "-vm", str(vad_model_path)]

    def _beam_size_for(self, is_final: bool) -> int:
        return self.final_beam_size if is_final else self.partial_beam_size


def select_best_ko_es_result(transcripts: dict[str, str]) -> tuple[str, str]:
    best_language = ""
    best_text = ""
    best_score = float("-inf")

    for language, text in transcripts.items():
        stripped = text.strip()
        if not stripped:
            continue
        if _contains_unsupported_script(stripped):
            continue

        score = _score_text_for_language(stripped, language)
        if score > best_score or (score == best_score and len(stripped) > len(best_text)):
            best_language = language
            best_text = stripped
            best_score = score

    if best_language:
        return best_language, best_text

    return "", ""


def infer_best_ko_es_language(text: str) -> str:
    stripped = text.strip()
    if not stripped:
        return "unknown"

    ko_score = _score_text_for_language(stripped, "ko")
    es_score = _score_text_for_language(stripped, "es")
    return "ko" if ko_score >= es_score else "es"


def should_retry_restricted_auto(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return False

    if _contains_unsupported_script(stripped):
        return True

    ko_score = _score_text_for_language(stripped, "ko")
    es_score = _score_text_for_language(stripped, "es")
    return abs(ko_score - es_score) < 1.5


def _score_text_for_language(text: str, language: str) -> float:
    lowered = f" {text.lower()} "
    hallucination_penalty = -40.0 if _normalize_hallucination_key(text) in KNOWN_HALLUCINATION_KEYS else 0.0
    hangul = sum(1 for char in text if "\uac00" <= char <= "\ud7a3")
    hiragana = sum(1 for char in text if "\u3040" <= char <= "\u309f")
    katakana = sum(1 for char in text if "\u30a0" <= char <= "\u30ff")
    han = sum(1 for char in text if "\u4e00" <= char <= "\u9fff")
    accents = sum(1 for char in text if char in "áéíóúüñÁÉÍÓÚÜÑ")
    latin = sum(1 for char in text if _is_latin_character(char))
    letters = max(hangul + hiragana + katakana + han + latin, 1)
    spanish_markers = sum(lowered.count(marker) for marker in SPANISH_TEXT_MARKERS)
    words = _tokenize_words(text)
    word_count = max(len(words), 1)
    spanish_stopword_hits = sum(1 for word in words if word in SPANISH_STOPWORDS)
    korean_particle_hits = sum(1 for word in words if word.endswith(KOREAN_PARTICLE_ENDINGS))
    korean_common_hits = sum(1 for word in words if word in KOREAN_COMMON_WORDS)
    latin_word_hits = sum(1 for word in words if _is_ascii_word(word))

    hangul_ratio = hangul / letters
    latin_ratio = latin / letters
    spanish_marker_ratio = spanish_markers / word_count
    spanish_stopword_ratio = spanish_stopword_hits / word_count
    korean_particle_ratio = korean_particle_hits / word_count
    korean_common_ratio = korean_common_hits / word_count
    latin_word_ratio = latin_word_hits / word_count

    if language == "ko":
        return (
            hallucination_penalty
            + (hangul_ratio * 14.0)
            + (korean_particle_ratio * 18.0)
            + (korean_common_ratio * 14.0)
            - (latin_word_ratio * 8.0)
            - (spanish_stopword_ratio * 12.0)
            - (hiragana / letters * 7.0)
            - (katakana / letters * 7.0)
            - (han / letters * 5.0)
        )

    if language == "es":
        return (
            hallucination_penalty
            + (latin_ratio * 10.0)
            + (accents / letters * 5.0)
            + (spanish_marker_ratio * 18.0)
            + (spanish_stopword_ratio * 20.0)
            - (hangul_ratio * 14.0)
            - (korean_particle_ratio * 10.0)
            - (hiragana / letters * 9.0)
            - (katakana / letters * 9.0)
            - (han / letters * 8.0)
        )

    return float(len(text))


def _is_latin_character(char: str) -> bool:
    return ("a" <= char.lower() <= "z") or char in "áéíóúüñÁÉÍÓÚÜÑ"


def _tokenize_words(text: str) -> list[str]:
    return [token.casefold() for token in re.findall(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+|[가-힣]+", text)]


def _is_ascii_word(token: str) -> bool:
    return all("a" <= char <= "z" for char in token.casefold())


def _contains_unsupported_script(text: str) -> bool:
    for char in text:
        codepoint = ord(char)
        if 0x3040 <= codepoint <= 0x30FF:
            return True
        if 0x4E00 <= codepoint <= 0x9FFF:
            return True
        if 0x0B80 <= codepoint <= 0x0BFF:
            return True
    return False


def _normalize_hallucination_key(text: str) -> str:
    return re.sub(r"[^0-9A-Za-z가-힣]+", "", text).casefold()


def parse_detected_language_output(output: str) -> tuple[str, float]:
    match = re.search(
        r"auto-detected language:\s+([a-z]{2})\s+\(p\s*=\s*([0-9.]+)\)",
        output,
    )
    if not match:
        return "", 0.0
    return match.group(1), float(match.group(2))
