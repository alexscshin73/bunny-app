from app.services.translate.base import Translator, TranslatorBackendStatus
from app.services.translation_guardrails import canonicalize_source_text, stabilize_translations


class GuardrailedTranslator(Translator):
    def __init__(self, inner: Translator) -> None:
        self.inner = inner

    def status(self) -> TranslatorBackendStatus:
        status = self.inner.status()
        details = dict(status.details)
        details["guardrails"] = True
        return TranslatorBackendStatus(
            engine=status.engine,
            ready=status.ready,
            details=details,
        )

    async def translate_all(
        self,
        text: str,
        source_language: str,
        target_languages: list[str],
        *,
        mode: str = "quality",
    ) -> dict[str, str]:
        canonical_source = canonicalize_source_text(text, language=source_language)
        translations = await self.inner.translate_all(
            text=canonical_source,
            source_language=source_language,
            target_languages=target_languages,
            mode=mode,
        )
        return stabilize_translations(
            source_text=canonical_source,
            source_language=source_language,
            translations=translations,
        )
