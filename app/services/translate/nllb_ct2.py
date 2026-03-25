import asyncio
import importlib.util
import inspect
import threading
from collections import OrderedDict
from pathlib import Path

from app.services.translate.base import Translator, TranslatorBackendStatus

NLLB_LANGUAGE_CODES = {
    "es": "spa_Latn",
    "ko": "kor_Hang",
}

SPANISH_HINTS = (
    " el ",
    " la ",
    " los ",
    " las ",
    " un ",
    " una ",
    " que ",
    " de ",
    " y ",
    " en ",
    " por ",
    " para ",
)

class NllbCTranslate2Translator(Translator):
    def __init__(
        self,
        model_path: str | None,
        tokenizer_path: str | None,
        device: str = "cpu",
        compute_type: str = "int8",
        inter_threads: int = 1,
        intra_threads: int = 0,
        default_targets: list[str] | None = None,
        cache_max_entries: int = 256,
    ) -> None:
        self.model_path = model_path
        self.tokenizer_path = tokenizer_path
        self.device = device
        self.compute_type = compute_type
        self.inter_threads = inter_threads
        self.intra_threads = intra_threads
        self.default_targets = default_targets or ["ko", "es"]
        self._runtime_lock = threading.Lock()
        self._translator = None
        self._tokenizer = None
        self._cache_max_entries = max(cache_max_entries, 0)
        self._translation_cache: OrderedDict[tuple[str, str, tuple[str, ...], str], dict[str, str]] = OrderedDict()

    def status(self) -> TranslatorBackendStatus:
        model_dir = self._resolve_model_path()
        tokenizer_dir = self._resolve_tokenizer_path()
        deps_ready = self._deps_available()

        return TranslatorBackendStatus(
            engine="nllb_ct2",
            ready=bool(deps_ready and model_dir and tokenizer_dir),
            details={
                "model_path": str(model_dir) if model_dir else None,
                "model_found": bool(model_dir),
                "tokenizer_path": str(tokenizer_dir) if tokenizer_dir else None,
                "tokenizer_found": bool(tokenizer_dir),
                "deps_ready": deps_ready,
                "device": self.device,
                "compute_type": self.compute_type,
            },
        )

    async def translate_all(
        self,
        text: str,
        source_language: str,
        target_languages: list[str],
        *,
        mode: str = "quality",
    ) -> dict[str, str]:
        stripped = text.strip()
        if not stripped:
            return {}

        targets = target_languages or self.default_targets
        source_iso = self._resolve_source_language(source_language, stripped)
        ordered_targets = self._ordered_targets(targets)
        cache_key = (stripped, source_iso, tuple(ordered_targets), mode)
        cached = self._cache_get(cache_key)
        if cached is not None:
            return cached

        translations = await asyncio.to_thread(
            self._translate_sync,
            stripped,
            source_iso,
            ordered_targets,
            mode,
        )
        self._cache_put(cache_key, translations)
        return dict(translations)

    def _translate_sync(
        self,
        text: str,
        source_iso: str,
        target_languages: list[str],
        mode: str,
    ) -> dict[str, str]:
        self._ensure_runtime()

        assert self._translator is not None
        assert self._tokenizer is not None

        source_code = self._to_nllb_code(source_iso)
        self._tokenizer.src_lang = source_code
        source_tokens = self._tokenizer.convert_ids_to_tokens(self._tokenizer.encode(text))

        pending_targets = [target for target in target_languages if target != source_iso]
        translations = {source_iso: text} if source_iso in target_languages else {}

        if not pending_targets:
            return {target: translations[target] for target in target_languages}

        beam_size = _beam_size_for(source_tokens, mode)
        max_decoding_length = _max_decoding_length_for(source_tokens)
        target_prefix = [[self._to_nllb_code(target)] for target in pending_targets]
        results = self._translator.translate_batch(
            [source_tokens] * len(pending_targets),
            target_prefix=target_prefix,
            beam_size=beam_size,
            repetition_penalty=1.18,
            no_repeat_ngram_size=3,
            max_decoding_length=max_decoding_length,
        )

        for target, result in zip(pending_targets, results, strict=True):
            output_tokens = result.hypotheses[0][1:]
            output_ids = self._tokenizer.convert_tokens_to_ids(output_tokens)
            decoded = self._tokenizer.decode(output_ids, skip_special_tokens=True).strip()
            translations[target] = _clean_translation_output(decoded)

        return {target: translations[target] for target in target_languages}

    def _ensure_runtime(self) -> None:
        if self._translator is not None and self._tokenizer is not None:
            return

        with self._runtime_lock:
            if self._translator is not None and self._tokenizer is not None:
                return

            if not self._deps_available():
                raise RuntimeError(
                    "NLLB/CTranslate2 dependencies are missing. Install ctranslate2, transformers, and sentencepiece."
                )

            model_path = self._require_model_path()
            tokenizer_path = self._require_tokenizer_path()

            import ctranslate2
            from transformers import AutoTokenizer

            self._translator = ctranslate2.Translator(
                str(model_path),
                device=self.device,
                compute_type=self.compute_type,
                inter_threads=self.inter_threads,
                intra_threads=self.intra_threads,
            )
            tokenizer_kwargs = {"src_lang": "spa_Latn"}
            if "fix_mistral_regex" in inspect.signature(AutoTokenizer.from_pretrained).parameters:
                tokenizer_kwargs["fix_mistral_regex"] = True
            self._tokenizer = AutoTokenizer.from_pretrained(str(tokenizer_path), **tokenizer_kwargs)

    def _deps_available(self) -> bool:
        return all(
            importlib.util.find_spec(module_name) is not None
            for module_name in ("ctranslate2", "transformers", "sentencepiece")
        )

    def _resolve_model_path(self) -> Path | None:
        if not self.model_path:
            return None
        candidate = Path(self.model_path).expanduser()
        if candidate.is_dir() and (candidate / "model.bin").exists():
            return candidate
        return None

    def _resolve_tokenizer_path(self) -> Path | None:
        if self.tokenizer_path:
            candidate = Path(self.tokenizer_path).expanduser()
            if candidate.exists():
                return candidate

        model_dir = self._resolve_model_path()
        if model_dir and any((model_dir / filename).exists() for filename in _TOKENIZER_FILES):
            return model_dir
        return None

    def _require_model_path(self) -> Path:
        model_path = self._resolve_model_path()
        if model_path:
            return model_path
        raise RuntimeError(
            "NLLB CTranslate2 model not found. Set BUNNY_TRANSLATION_MODEL_PATH to a converted model directory containing model.bin."
        )

    def _require_tokenizer_path(self) -> Path:
        tokenizer_path = self._resolve_tokenizer_path()
        if tokenizer_path:
            return tokenizer_path
        raise RuntimeError(
            "NLLB tokenizer files not found. Set BUNNY_TRANSLATION_TOKENIZER_PATH to a local tokenizer directory."
        )

    def _resolve_source_language(self, source_language: str, text: str) -> str:
        normalized = source_language.strip().lower() if source_language else ""
        if normalized in NLLB_LANGUAGE_CODES:
            return normalized
        if normalized in NLLB_LANGUAGE_CODES.values():
            return _invert_language_codes()[normalized]
        return detect_text_language(text)

    def _ordered_targets(self, target_languages: list[str]) -> list[str]:
        ordered_targets: list[str] = []
        for target in target_languages:
            if target not in ordered_targets:
                ordered_targets.append(target)
        return ordered_targets

    def _cache_get(self, key: tuple[str, str, tuple[str, ...], str]) -> dict[str, str] | None:
        if self._cache_max_entries <= 0:
            return None
        with self._runtime_lock:
            cached = self._translation_cache.get(key)
            if cached is None:
                return None
            self._translation_cache.move_to_end(key)
            return dict(cached)

    def _cache_put(self, key: tuple[str, str, tuple[str, ...], str], value: dict[str, str]) -> None:
        if self._cache_max_entries <= 0:
            return
        with self._runtime_lock:
            self._translation_cache[key] = dict(value)
            self._translation_cache.move_to_end(key)
            while len(self._translation_cache) > self._cache_max_entries:
                self._translation_cache.popitem(last=False)

    def _to_nllb_code(self, language: str) -> str:
        try:
            return NLLB_LANGUAGE_CODES[language]
        except KeyError as exc:
            raise RuntimeError(f"Unsupported translation language: {language}") from exc


def detect_text_language(text: str) -> str:
    if any("\uac00" <= char <= "\ud7a3" for char in text):
        return "ko"

    lowered = f" {text.lower()} "
    if any(hint in lowered for hint in SPANISH_HINTS) or any(char in lowered for char in "áéíóúñ¿¡"):
        return "es"
    return "es"


def _invert_language_codes() -> dict[str, str]:
    return {value: key for key, value in NLLB_LANGUAGE_CODES.items()}


def _clean_translation_output(text: str) -> str:
    stripped = text.strip()
    if not stripped:
        return ""

    tokens = stripped.split()
    if len(tokens) < 4:
        return stripped

    cleaned_tokens: list[str] = []
    previous_normalized = ""
    repeated = 0

    for token in tokens:
        normalized = token.strip(".,!?;:[](){}\"'`").lower()
        if normalized and normalized == previous_normalized:
            repeated += 1
            continue
        previous_normalized = normalized
        cleaned_tokens.append(token)

    if repeated == 0:
        return stripped

    return " ".join(cleaned_tokens).strip()


def _max_decoding_length_for(source_tokens: list[str]) -> int:
    token_count = len(source_tokens)
    if token_count <= 2:
        return 8
    if token_count <= 4:
        return 12
    if token_count <= 8:
        return 18
    return max(32, token_count * 3)


def _beam_size_for(source_tokens: list[str], mode: str) -> int:
    token_count = len(source_tokens)
    if mode == "realtime":
        return 2 if token_count <= 6 else 3
    if token_count <= 4:
        return 4
    return 5


_TOKENIZER_FILES = (
    "tokenizer.json",
    "tokenizer_config.json",
    "sentencepiece.bpe.model",
)
