import io
import shutil
import subprocess
from tempfile import TemporaryDirectory
from pathlib import Path
import wave

from app.config import Settings
from app.services.llm_postedit import TranslationPolisher
from app.services.nonverbal import is_nonverbal_text
from app.services.pipeline import build_asr, build_translation_polisher, build_translator
from app.services.translation_guardrails import canonicalize_source_text
from app.services.translation_guardrails import stabilize_translations


class UploadedAudioProcessingError(RuntimeError):
    pass


async def process_uploaded_audio_turn(
    settings: Settings,
    audio_bytes: bytes,
    filename: str | None,
    content_type: str | None,
    source_language: str,
) -> tuple[str, dict[str, str], str]:
    pcm_bytes, sample_rate = decode_audio_to_pcm16le(
        audio_bytes=audio_bytes,
        filename=filename,
        content_type=content_type,
    )

    asr = build_asr(settings)
    translator = build_translator(settings)
    polisher = build_translation_polisher(settings)

    result = await asr.transcribe_chunk(
        pcm_chunk=pcm_bytes,
        sample_rate=sample_rate,
        language=source_language,
        is_final=True,
    )
    text = result.text.strip()
    if not text:
        raise UploadedAudioProcessingError("No speech was detected in the uploaded audio.")
    text = canonicalize_source_text(text, language=result.language)

    if is_nonverbal_text(text):
        return text, {}, result.language

    translations = await translator.translate_all(
        text=text,
        source_language=result.language,
        target_languages=settings.translation_targets,
        mode="quality",
    )
    translations = stabilize_translations(
        source_text=text,
        source_language=result.language,
        translations=translations,
    )
    translations = await _polish_translations(
        polisher=polisher,
        source_text=text,
        source_language=result.language,
        translations=translations,
    )
    translations = stabilize_translations(
        source_text=text,
        source_language=result.language,
        translations=translations,
    )
    return text, translations, result.language


async def process_demo_text_turn(
    settings: Settings,
    source_text: str,
    source_language: str,
) -> tuple[str, dict[str, str], str]:
    text = source_text.strip()
    if not text:
        raise UploadedAudioProcessingError("Demo text cannot be empty.")
    text = canonicalize_source_text(text, language=source_language)

    if is_nonverbal_text(text):
        return text, {}, source_language

    translator = build_translator(settings)
    polisher = build_translation_polisher(settings)
    translations = await translator.translate_all(
        text=text,
        source_language=source_language,
        target_languages=settings.translation_targets,
        mode="quality",
    )
    translations = stabilize_translations(
        source_text=text,
        source_language=source_language,
        translations=translations,
    )
    translations = await _polish_translations(
        polisher=polisher,
        source_text=text,
        source_language=source_language,
        translations=translations,
    )
    translations = stabilize_translations(
        source_text=text,
        source_language=source_language,
        translations=translations,
    )
    return text, translations, source_language


def decode_audio_to_pcm16le(
    audio_bytes: bytes,
    filename: str | None,
    content_type: str | None,
) -> tuple[bytes, int]:
    try:
        return _decode_wav_if_supported(audio_bytes)
    except UploadedAudioProcessingError:
        return _decode_with_ffmpeg(audio_bytes, filename, content_type)


async def _polish_translations(
    polisher: TranslationPolisher | None,
    source_text: str,
    source_language: str,
    translations: dict[str, str],
) -> dict[str, str]:
    if not polisher:
        return translations

    polished = dict(translations)
    for target_language, draft in translations.items():
        if target_language == source_language or not draft.strip():
            continue
        polished[target_language] = await polisher.polish_translation(
            source_text=source_text,
            source_language=source_language,
            target_language=target_language,
            draft_translation=draft,
            conversation_history=[],
        )
    return polished


def _decode_wav_if_supported(audio_bytes: bytes) -> tuple[bytes, int]:
    try:
        with wave.open(io.BytesIO(audio_bytes), "rb") as wav_file:
            channels = wav_file.getnchannels()
            sample_width = wav_file.getsampwidth()
            sample_rate = wav_file.getframerate()
            frames = wav_file.readframes(wav_file.getnframes())
    except (wave.Error, EOFError) as exc:
        raise UploadedAudioProcessingError("Uploaded audio is not a directly supported WAV file.") from exc

    if channels != 1 or sample_width != 2 or sample_rate != 16000:
        raise UploadedAudioProcessingError(
            "WAV upload must already be mono 16-bit PCM at 16000 Hz unless ffmpeg is available."
        )

    return frames, sample_rate


def _decode_with_ffmpeg(
    audio_bytes: bytes,
    filename: str | None,
    content_type: str | None,
) -> tuple[bytes, int]:
    ffmpeg_binary = shutil.which("ffmpeg")
    if not ffmpeg_binary:
        raise UploadedAudioProcessingError(
            "ffmpeg is required to process this uploaded audio format on the server."
        )

    suffix = Path(filename or "upload.bin").suffix or _suffix_from_content_type(content_type)
    with TemporaryDirectory(prefix="bunny-app-upload-") as tmp_dir:
        tmp_path = Path(tmp_dir)
        input_path = tmp_path / f"input{suffix}"
        output_path = tmp_path / "output.pcm"
        input_path.write_bytes(audio_bytes)

        process = subprocess.run(
            [
                ffmpeg_binary,
                "-y",
                "-i",
                str(input_path),
                "-f",
                "s16le",
                "-acodec",
                "pcm_s16le",
                "-ac",
                "1",
                "-ar",
                "16000",
                str(output_path),
            ],
            capture_output=True,
            check=False,
        )
        if process.returncode != 0:
            error_text = process.stderr.decode("utf-8", errors="ignore").strip()
            raise UploadedAudioProcessingError(f"ffmpeg failed to decode uploaded audio: {error_text}")

        return output_path.read_bytes(), 16000


def _suffix_from_content_type(content_type: str | None) -> str:
    mapping = {
        "audio/mp4": ".m4a",
        "audio/x-m4a": ".m4a",
        "audio/aac": ".aac",
        "audio/webm": ".webm",
        "audio/wav": ".wav",
        "audio/x-wav": ".wav",
        "audio/mpeg": ".mp3",
    }
    return mapping.get((content_type or "").lower(), ".bin")
