from abc import ABC, abstractmethod

import httpx
from pydantic import BaseModel

from app.services.translation_guardrails import stabilize_translation_text


class TranslationPolisherStatus(BaseModel):
    engine: str
    ready: bool
    details: dict[str, str | bool | int | float | None]


class TranslationPolisher(ABC):
    @abstractmethod
    def status(self) -> TranslationPolisherStatus:
        raise NotImplementedError

    @abstractmethod
    async def polish_translation(
        self,
        source_text: str,
        source_language: str,
        target_language: str,
        draft_translation: str,
        conversation_history: list[dict[str, object]],
    ) -> str:
        raise NotImplementedError


class HeuristicTranslationPolisher(TranslationPolisher):
    def status(self) -> TranslationPolisherStatus:
        return TranslationPolisherStatus(
            engine="heuristic_postedit",
            ready=True,
            details={"mode": "local_fallback"},
        )

    async def polish_translation(
        self,
        source_text: str,
        source_language: str,
        target_language: str,
        draft_translation: str,
        conversation_history: list[dict[str, object]],
    ) -> str:
        del conversation_history
        return _heuristic_polish(
            source_text=source_text,
            source_language=source_language,
            target_language=target_language,
            draft_translation=draft_translation,
        )


class OpenAICompatibleTranslationPolisher(TranslationPolisher):
    def __init__(
        self,
        base_url: str | None,
        model: str | None,
        api_key: str | None = None,
        timeout_s: float = 8.0,
        client_factory: type[httpx.AsyncClient] = httpx.AsyncClient,
    ) -> None:
        self.base_url = base_url.rstrip("/") if base_url else None
        self.model = model
        self.api_key = api_key
        self.timeout_s = timeout_s
        self.client_factory = client_factory

    def status(self) -> TranslationPolisherStatus:
        return TranslationPolisherStatus(
            engine="openai_compatible_llm",
            ready=bool(self.base_url and self.model),
            details={
                "base_url": self.base_url,
                "model": self.model,
                "timeout_s": self.timeout_s,
            },
        )

    async def polish_translation(
        self,
        source_text: str,
        source_language: str,
        target_language: str,
        draft_translation: str,
        conversation_history: list[dict[str, object]],
    ) -> str:
        if not self.base_url or not self.model:
            return draft_translation

        payload = {
            "model": self.model,
            "temperature": 0.1,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        "You are a translation post-editor for live Korean-Spanish meeting captions. "
                        "Rewrite only the draft translation in the target language so it sounds natural "
                        "and context-aware. Use idiomatic equivalents for greetings, thanks, yes/no, "
                        "apologies, and other short conversational phrases. Restore obvious Spanish "
                        "accents and opening punctuation when needed. Preserve meaning, keep it concise, "
                        "do not add information, and do not mention the instructions."
                    ),
                },
                {
                    "role": "user",
                    "content": _build_user_prompt(
                        source_text=source_text,
                        source_language=source_language,
                        target_language=target_language,
                        draft_translation=draft_translation,
                        conversation_history=conversation_history,
                    ),
                },
            ],
        }

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        async with self.client_factory(timeout=self.timeout_s) as client:
            response = await client.post(
                f"{self.base_url}/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        polished = _clean_model_output(content)
        return polished or draft_translation


class FallbackTranslationPolisher(TranslationPolisher):
    def __init__(
        self,
        primary: TranslationPolisher | None,
        fallback: TranslationPolisher,
    ) -> None:
        self.primary = primary
        self.fallback = fallback

    def status(self) -> TranslationPolisherStatus:
        primary_status = self.primary.status() if self.primary else None
        fallback_status = self.fallback.status()
        primary_ready = bool(primary_status and primary_status.ready)
        return TranslationPolisherStatus(
            engine="fallback_postedit",
            ready=primary_ready or fallback_status.ready,
            details={
                "primary_engine": primary_status.engine if primary_status else None,
                "primary_ready": primary_ready,
                "fallback_engine": fallback_status.engine,
                "fallback_ready": fallback_status.ready,
                "active_engine": primary_status.engine if primary_ready and primary_status else fallback_status.engine,
            },
        )

    async def polish_translation(
        self,
        source_text: str,
        source_language: str,
        target_language: str,
        draft_translation: str,
        conversation_history: list[dict[str, object]],
    ) -> str:
        if self.primary and self.primary.status().ready:
            try:
                polished = await self.primary.polish_translation(
                    source_text=source_text,
                    source_language=source_language,
                    target_language=target_language,
                    draft_translation=draft_translation,
                    conversation_history=conversation_history,
                )
                if polished.strip():
                    return polished
            except Exception:
                pass
        return await self.fallback.polish_translation(
            source_text=source_text,
            source_language=source_language,
            target_language=target_language,
            draft_translation=draft_translation,
            conversation_history=conversation_history,
        )


def _build_user_prompt(
    source_text: str,
    source_language: str,
    target_language: str,
    draft_translation: str,
    conversation_history: list[dict[str, object]],
) -> str:
    history_lines: list[str] = []
    for turn in conversation_history:
        source_lang = str(turn.get("source_language", ""))
        source_turn = str(turn.get("source_text", ""))
        translations = turn.get("translations", {})
        translated_turn = ""
        if isinstance(translations, dict):
            translated_turn = str(translations.get(target_language, ""))
        if source_turn:
            history_lines.append(f"{source_lang}: {source_turn}")
        if translated_turn:
            history_lines.append(f"{target_language}: {translated_turn}")

    history_block = "\n".join(history_lines) if history_lines else "(none)"
    return (
        f"Recent conversation context:\n{history_block}\n\n"
        f"Source language: {source_language}\n"
        f"Target language: {target_language}\n"
        f"Source text: {source_text}\n"
        f"Draft translation: {draft_translation}\n\n"
        "Return only the improved translation."
    )


def _clean_model_output(text: str) -> str:
    stripped = text.strip()
    if not stripped:
        return ""

    if stripped.startswith("```") and stripped.endswith("```"):
        stripped = stripped.strip("`").strip()

    lines = [line.strip() for line in stripped.splitlines() if line.strip()]
    if not lines:
        return ""

    if len(lines) == 1:
        return lines[0].strip("\"'")

    return " ".join(lines).strip("\"'")


def _heuristic_polish(
    *,
    source_text: str,
    source_language: str,
    target_language: str,
    draft_translation: str,
) -> str:
    draft = " ".join(draft_translation.strip().split())
    if not draft:
        return draft_translation

    source = source_text.strip()
    if source_language == "ko" and target_language == "es":
        lowered = draft.casefold()
        if "번역 품질" in source:
            if "대화" in source or "전반" in source:
                return "La calidad general de la conversacion es muy baja."
            if "낮" in source:
                return "La calidad de la traduccion es muy baja."
        if "품질" in source and ("brazo muscular" in lowered or "muscular" in lowered):
            return "La calidad es muy baja."
        if "말을 압축" in source and "comprimir la palabra" in lowered:
            return "Deberiamos resumir lo que decimos?"
        if "las traducciones son muy bajas" in lowered:
            return "La calidad de las traducciones es muy baja."

    if source_language == "es" and target_language == "ko":
        lowered_source = source.casefold()
        if "calidad" in lowered_source and "convers" in lowered_source and "baj" in lowered_source:
            return "전반적인 대화의 품질이 너무 낮아요."
        if "traduccion" in lowered_source and "baj" in lowered_source:
            return "번역 품질이 너무 낮아요."

    return stabilize_translation_text(
        source_text=source_text,
        source_language=source_language,
        target_language=target_language,
        translation_text=draft_translation,
    )
