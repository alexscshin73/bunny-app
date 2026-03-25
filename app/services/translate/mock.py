from app.services.translate.base import Translator, TranslatorBackendStatus


class MockTranslator(Translator):
    def __init__(self, default_targets: list[str]) -> None:
        self.default_targets = default_targets

    def status(self) -> TranslatorBackendStatus:
        return TranslatorBackendStatus(
            engine="mock",
            ready=True,
            details={"mode": "simulated"},
        )

    async def translate_all(
        self,
        text: str,
        source_language: str,
        target_languages: list[str],
        *,
        mode: str = "quality",
    ) -> dict[str, str]:
        translations: dict[str, str] = {}
        targets = target_languages or self.default_targets

        for target in targets:
            if target == source_language:
                translations[target] = text
                continue
            translations[target] = f"[{source_language}->{target}] {text}"

        return translations
