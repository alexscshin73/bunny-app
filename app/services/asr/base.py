from abc import ABC, abstractmethod

from pydantic import BaseModel


class AsrResult(BaseModel):
    text: str
    language: str
    is_final: bool = False


class AsrBackendStatus(BaseModel):
    engine: str
    ready: bool
    details: dict[str, str | bool | int | float | None]


class StreamingAsr(ABC):
    @abstractmethod
    def status(self) -> AsrBackendStatus:
        raise NotImplementedError

    @abstractmethod
    async def transcribe_chunk(
        self,
        pcm_chunk: bytes,
        sample_rate: int,
        language: str,
        is_final: bool,
    ) -> AsrResult:
        raise NotImplementedError
