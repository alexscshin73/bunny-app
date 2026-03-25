from abc import ABC, abstractmethod

from pydantic import BaseModel


class TranslatorBackendStatus(BaseModel):
    engine: str
    ready: bool
    details: dict[str, str | bool | int | None]


class Translator(ABC):
    @abstractmethod
    def status(self) -> TranslatorBackendStatus:
        raise NotImplementedError

    @abstractmethod
    async def translate_all(
        self,
        text: str,
        source_language: str,
        target_languages: list[str],
        *,
        mode: str = "quality",
    ) -> dict[str, str]:
        raise NotImplementedError
