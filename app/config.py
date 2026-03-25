from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Bunny App"
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: list[str] = Field(default_factory=lambda: ["*"])
    asr_engine: str = "mock"
    whisper_cpp_binary: str | None = None
    whisper_model_path: str | None = None
    whisper_language: str = "auto"
    whisper_cpp_no_gpu: bool = False
    whisper_cpp_use_vad: bool = False
    whisper_vad_model_path: str | None = None
    whisper_cpp_suppress_non_speech: bool = True
    whisper_cpp_no_fallback: bool = False
    whisper_threads: int = 4
    whisper_processors: int = 1
    whisper_partial_beam_size: int = 3
    whisper_final_beam_size: int = 7
    whisper_no_speech_threshold: float = 0.8
    whisper_logprob_threshold: float = -0.5
    whisper_entropy_threshold: float = 2.2
    vad_enabled: bool = True
    vad_energy_threshold: float = 0.01
    vad_silence_ms: int = 550
    vad_min_speech_ms: int = 400
    vad_preroll_ms: int = 400
    utterance_max_ms: int = 8000
    segment_emit_ms: int = 650
    segment_emit_bytes: int = 32_000
    partial_preview_ms: int = 2800
    translation_engine: str = "mock"
    translation_model_path: str | None = None
    translation_tokenizer_path: str | None = None
    translation_device: str = "cpu"
    translation_compute_type: str = "int8"
    translation_inter_threads: int = 2
    translation_intra_threads: int = 0
    translation_targets: list[str] = Field(default_factory=lambda: ["ko", "es"])
    llm_postedit_enabled: bool = False
    llm_postedit_base_url: str | None = None
    llm_postedit_api_key: str | None = None
    llm_postedit_model: str | None = None
    llm_postedit_timeout_s: float = 8.0
    llm_postedit_history_turns: int = 4
    llm_postedit_scope: Literal["final", "all"] = "final"
    room_store_backend: str = "sqlite"
    room_store_path: str = "data/bunny_app.sqlite3"
    room_store_url: str | None = None
    room_max_participants: int = 5
    room_ttl_minutes: int = 1440
    room_cleanup_interval_seconds: int = 300
    web_push_public_key: str | None = None
    web_push_private_key: str | None = None
    web_push_subject: str | None = None

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="BUNNY_",
        case_sensitive=False,
    )

    @field_validator("cors_origins", "translation_targets", mode="before")
    @classmethod
    def parse_csv_or_list(cls, value: object) -> object:
        if isinstance(value, str):
            stripped = value.strip()
            if not stripped:
                return []
            if stripped.startswith("["):
                return value
            return [item.strip() for item in stripped.split(",") if item.strip()]
        return value


@lru_cache
def get_settings() -> Settings:
    return Settings()
