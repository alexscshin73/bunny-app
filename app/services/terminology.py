from __future__ import annotations

from dataclasses import dataclass
import re


SUPPORTED_TERM_LANGUAGES = {"ko", "es"}


@dataclass(frozen=True)
class TerminologyEntry:
    key: str
    canonical: dict[str, str]
    aliases: dict[str, tuple[str, ...]]


TERMINOLOGY_ENTRIES: tuple[TerminologyEntry, ...] = (
    TerminologyEntry(
        key="cartel",
        canonical={
            "ko": "카르텔",
            "es": "cartel",
        },
        aliases={
            "ko": ("카르텔", "카르트리", "카르테리"),
            "es": ("cartel", "cártel", "carteri"),
        },
    ),
    TerminologyEntry(
        key="obispado",
        canonical={
            "ko": "오비스파도",
            "es": "obispado",
        },
        aliases={
            "ko": ("오비스파도", "오비스파도", "오비스빠도", "오비수파도"),
            "es": ("obispado", "obispados"),
        },
    ),
)


def normalize_source_terms(text: str, language: str) -> str:
    if language not in SUPPORTED_TERM_LANGUAGES or not text.strip():
        return text

    normalized = text
    for entry in TERMINOLOGY_ENTRIES:
        canonical = entry.canonical.get(language)
        if not canonical:
            continue
        normalized = _replace_aliases_with_term(
            text=normalized,
            language=language,
            entry=entry,
            replacement=canonical,
        )
    return normalized


def enforce_translation_terms(
    *,
    source_text: str,
    source_language: str,
    target_language: str,
    translation_text: str,
    conversation_history: list[dict[str, object]],
) -> str:
    if (
        source_language not in SUPPORTED_TERM_LANGUAGES
        or target_language not in SUPPORTED_TERM_LANGUAGES
        or not translation_text.strip()
    ):
        return translation_text

    remembered_terms = _remembered_target_terms(
        conversation_history=conversation_history,
        source_language=source_language,
        target_language=target_language,
    )
    normalized = translation_text

    for entry in TERMINOLOGY_ENTRIES:
        if not _contains_term_alias(source_text, source_language, entry):
            continue
        replacement = remembered_terms.get(entry.key) or entry.canonical.get(target_language)
        if not replacement:
            continue
        normalized = _replace_aliases_with_term(
            text=normalized,
            language=target_language,
            entry=entry,
            replacement=replacement,
        )

    return normalized


def _remembered_target_terms(
    *,
    conversation_history: list[dict[str, object]],
    source_language: str,
    target_language: str,
) -> dict[str, str]:
    remembered: dict[str, str] = {}

    for turn in reversed(conversation_history):
        if str(turn.get("source_language", "")) != source_language:
            continue
        source_text = str(turn.get("source_text", ""))
        translations = turn.get("translations", {})
        if not isinstance(translations, dict):
            continue
        translated_text = str(translations.get(target_language, ""))
        if not translated_text:
            continue

        for entry in TERMINOLOGY_ENTRIES:
            if entry.key in remembered:
                continue
            if not _contains_term_alias(source_text, source_language, entry):
                continue
            matched_target = _find_matching_alias_surface(translated_text, target_language, entry)
            if matched_target:
                remembered[entry.key] = matched_target

    return remembered


def _contains_term_alias(text: str, language: str, entry: TerminologyEntry) -> bool:
    return _find_matching_alias_surface(text, language, entry) is not None


def _find_matching_alias_surface(text: str, language: str, entry: TerminologyEntry) -> str | None:
    aliases = entry.aliases.get(language, ())
    if not aliases:
        return None

    if language == "es":
        lowered = text.casefold()
        for alias in aliases:
            pattern = re.compile(rf"\b{re.escape(alias)}\b", re.IGNORECASE)
            match = pattern.search(text)
            if match:
                return match.group(0)
            if alias.casefold() in lowered:
                return alias
        return None

    for alias in sorted(aliases, key=len, reverse=True):
        if alias in text:
            return alias
    return None


def _replace_aliases_with_term(
    *,
    text: str,
    language: str,
    entry: TerminologyEntry,
    replacement: str,
) -> str:
    aliases = entry.aliases.get(language, ())
    if not aliases:
        return text

    normalized = text
    if language == "es":
        for alias in aliases:
            pattern = re.compile(rf"\b{re.escape(alias)}\b", re.IGNORECASE)
            normalized = pattern.sub(replacement, normalized)
        return normalized

    for alias in sorted(aliases, key=len, reverse=True):
        normalized = normalized.replace(alias, replacement)
    return normalized
