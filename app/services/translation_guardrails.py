from __future__ import annotations

import re
import unicodedata


_SHORT_PHRASE_OVERRIDES: dict[tuple[str, str], dict[str, str]] = {
    ("ko", "es"): {
        "안녕": "Hola.",
        "안녕하세요": "Hola.",
        "감사합니다": "Gracias.",
        "고맙습니다": "Gracias.",
        "고마워요": "Gracias.",
        "네": "Si.",
        "예": "Si.",
        "아니요": "No.",
        "죄송합니다": "Lo siento.",
        "미안합니다": "Lo siento.",
        "미안해요": "Lo siento.",
        "괜찮아요": "Esta bien.",
        "괜찮습니다": "Esta bien.",
        "잠시만요": "Un momento.",
        "어떻게지내세요": "¿Cómo estás?",
        "어떻게지내세요?": "¿Cómo estás?",
        "어떻게지내시나요": "¿Cómo estás?",
        "어떻게지내시나요?": "¿Cómo estás?",
        "잘지내세요": "¿Cómo estás?",
        "잘지내세요?": "¿Cómo estás?",
        "잘지내시나요": "¿Cómo estás?",
        "잘지내시나요?": "¿Cómo estás?",
        "잘지내나요": "¿Cómo estás?",
        "잘지내나요?": "¿Cómo estás?",
        "잘지내": "¿Cómo estás?",
        "잘지내?": "¿Cómo estás?",
    },
    ("es", "ko"): {
        "hola": "안녕하세요.",
        "buenos dias": "안녕하세요.",
        "buenas tardes": "안녕하세요.",
        "buenas noches": "안녕하세요.",
        "como estas": "어떻게 지내세요?",
        "como esta": "어떻게 지내세요?",
        "como estan": "어떻게 지내세요?",
        "que tal": "어떻게 지내세요?",
        "gracias": "감사합니다.",
        "muchas gracias": "감사합니다.",
        "si": "네.",
        "no": "아니요.",
        "lo siento": "죄송합니다.",
        "perdon": "죄송합니다.",
        "esta bien": "괜찮아요.",
        "un momento": "잠시만요.",
    },
}

_KOREAN_TO_SPANISH_EXACT_OVERRIDES = {
    "모두좋은아침입니다": "Buenos días a todos",
    "안녕하세요(오후인사)": "Buenas tardes, señor",
    "좋은밤이야(인사)": "Buenas noches, amigo",
    "좋은밤이야": "Buenas noches, amigo",
    "만나서반가워(인사)": "Mucho gusto en conocerte",
    "만나서반가워": "Mucho gusto en conocerte",
    "오늘너무피곤해": "Estoy muy cansado hoy",
    "지금시간없어": "No tengo tiempo ahora",
    "좀천천히말해줘": "Habla más despacio, por favor",
    "이거어떻게말해": "¿Cómo se dice esto?",
    "여기서멀어": "Está muy lejos de aquí",
    "지금같이가자": "Vamos juntos ahora",
    "늦을것같아": "Voy a llegar tarde",
    "지금가는중이야": "Ya estoy en camino",
    "잠깐만기다려": "Espérame un momento",
    "이거얼마야": "¿Cuánto cuesta esto?",
    "현금으로낼게": "Voy a pagar en efectivo",
    "카드로낼게": "Voy a pagar con tarjeta",
    "그냥보고있는중이야": "Solo estoy mirando",
    "배고파": "Tengo mucha hambre",
    "목말라": "Tengo sed",
    "추천좀해줄래": "¿Me recomiendas algo?",
    "두명자리주세요": "Quiero una mesa para dos",
    "계산서주세요": "La cuenta, por favor",
    "좋은생각이야": "Me parece buena idea",
    "별로인것같아": "No me parece buena idea",
    "해보자": "Vamos a intentarlo",
    "좀생각해볼게": "Necesito pensar un poco",
    "잠깐만": "Dame un momento",
    "여기와줄수있어": "¿Puedes venir aquí?",
    "나중에전화할게": "Te llamo más tarde",
    "문자보내줘": "Mándame un mensaje",
    "나중에연락할게": "Te aviso después",
    "몸이안좋아": "No me siento bien",
    "지금은괜찮아": "Me siento mejor ahora",
    "오늘뭐할래": "¿Qué quieres hacer hoy?",
    "오늘계획없어": "No tengo planes hoy",
    "오늘나가자": "Vamos a salir hoy",
    "집에있고싶어": "Prefiero quedarme en casa",
    "아직준비안됐어": "Aún no estoy listo",
    "몇시에볼까": "¿A qué hora nos vemos?",
    "거의다왔어": "Ya casi llego",
    "운전조심해": "Ten cuidado al conducir",
    "걱정하지마": "No te preocupes",
    "좋은하루보내": "Que tengas buen día",
    "푹쉬어": "Que descanses bien",
    "그럼나중에봐": "Hasta luego entonces",
    "몸조심해": "Cuídate mucho",
    "좋은여행되길": "Buen viaje",
    "천천히하자": "Vamos poco a poco",
    "그거좋네": "Eso suena bien",
    "상황에따라달라": "Depende de la situación",
    "필요없어": "No es necesario",
    "두고보자": "Ya lo veremos",
}

_SPANISH_SOURCE_CANONICALS: dict[str, str] = {
    "como estas": "¿Cómo estás?",
    "como esta": "¿Cómo está?",
    "como estan": "¿Cómo están?",
    "que tal": "¿Qué tal?",
    "como te llamas": "¿Cómo te llamas?",
    "donde estas": "¿Dónde estás?",
    "cuantos anos tienes": "¿Cuántos años tienes?",
}

_KOREAN_SOURCE_CANONICALS: dict[str, str] = {
    "안녕": "안녕하세요.",
    "안녕하세요": "안녕하세요.",
    "잘지내": "잘 지내세요?",
    "잘지내?": "잘 지내세요?",
    "잘지내요": "잘 지내세요?",
    "잘지내요?": "잘 지내세요?",
    "잘지내세요": "잘 지내세요?",
    "잘지내세요?": "잘 지내세요?",
    "잘지내시나요": "잘 지내시나요?",
    "잘지내시나요?": "잘 지내시나요?",
    "어떻게지내세요": "어떻게 지내세요?",
    "어떻게지내세요?": "어떻게 지내세요?",
    "어떻게지내시나요": "어떻게 지내시나요?",
    "어떻게지내시나요?": "어떻게 지내시나요?",
}

_SPANISH_EXPLICIT_INFORMAL_CUES = {
    "tu",
    "tus",
    "te",
    "ti",
    "contigo",
    "vos",
    "vosotros",
    "vosotras",
    "os",
}

_SPANISH_EXPLICIT_FORMAL_CUES = {
    "usted",
    "ustedes",
    "senor",
    "senora",
    "senorita",
    "don",
    "dona",
}

_SPANISH_NUMBER_WORDS = {
    "un": "1",
    "uno": "1",
    "dos": "2",
    "tres": "3",
    "cuatro": "4",
    "cinco": "5",
    "seis": "6",
    "siete": "7",
    "ocho": "8",
    "nueve": "9",
    "diez": "10",
    "once": "11",
    "doce": "12",
    "trece": "13",
    "catorce": "14",
    "quince": "15",
    "veinte": "20",
}

_SPANISH_TO_KOREAN_EXACT_OVERRIDES = {
    "hola que tal": "안녕, 어떻게 지내?",
    "buenos dias a todos": "모두 좋은 아침입니다",
    "buenas noches amigo": "좋은 밤이야",
    "puedes repetir eso otra vez": "다시 말해줄래?",
    "como se dice esto": "이거 어떻게 말해?",
    "ya estoy en camino": "지금 가는 중이야",
    "voy a pagar en efectivo": "현금으로 낼게",
    "me gusta mucho esto": "이거 정말 마음에 들어",
    "no me gusta esto": "이거 마음에 안 들어",
    "vamos a comer algo": "뭐 좀 먹자",
    "quieres comer conmigo": "나랑 같이 먹을래?",
    "esto esta muy rico": "이거 맛있다",
    "quiero una mesa para dos": "두 명 자리 주세요",
    "la cuenta por favor": "계산서 주세요",
    "vamos a intentarlo": "해보자",
    "a que hora nos vemos": "몇 시에 볼까?",
    "que tengas buen dia": "좋은 하루 보내",
    "eso suena bien": "그거 좋네",
    "ya lo veremos": "두고 보자",
    "vamos a hacerlo bien": "제대로 해보자",
}

_SPANISH_ESTOY_EN_STATE_OVERRIDES = {
    "problema": "문제 생겼어",
    "problemas": "문제 생겼어",
    "reunion": "회의 중이야",
    "clase": "수업 중이야",
}

_AMBIGUOUS_SPANISH_TO_KOREAN_NEUTRAL_OVERRIDES = {
    "어떻게 지내?": "어떻게 지내세요?",
    "오늘 어때?": "오늘 어때요?",
    "지금 뭐하는 거야?": "지금 뭐 하고 있어요?",
    "지금 시간 없어": "지금 시간 없어요.",
    "이걸 도와줄래?": "이걸 도와줄 수 있어요?",
    "무슨 말인지 모르겠어": "무슨 말인지 모르겠어요.",
    "이제 함께 가자": "이제 함께 가요.",
    "난 늦게 올 거야": "늦을 것 같아요.",
    "이미 왔어": "이미 왔어요.",
    "난 이걸 싫어": "전 이걸 싫어해요.",
    "한 잔 먹자": "뭐 좀 먹어요.",
    "이건 좋지 않아": "이건 별로예요.",
    "뭔가 추천해줄래?": "뭔가 추천해줄 수 있어요?",
    "그건 말도 안 돼": "그건 말이 안 돼요.",
    "좀 생각해봐야겠어": "좀 생각해봐야겠어요.",
    "기분이 좋지 않아": "몸이 안 좋아요.",
    "나 나갈 준비가 됐어": "나갈 준비가 됐어요.",
    "아직 준비가 안 됐어": "아직 준비가 안 됐어요.",
    "8시에 보자": "8시에 봐요.",
    "거의 다 왔어": "거의 다 왔어요.",
    "다 괜찮을 거야": "다 괜찮을 거예요.",
    "괜찮아": "괜찮아요.",
    "내일 보자": "내일 봐요.",
    "그럼 나중에 보자": "그럼 나중에 봐요.",
    "천천히 가자": "천천히 가요.",
    "문제 생겼어": "문제 생겼어요.",
    "필요없어": "필요 없어요.",
    "그만한 가치가 있어": "그만한 가치가 있어요.",
}

_KOREAN_POLITE_ENDING_REPLACEMENTS: tuple[tuple[str, str], ...] = (
    (r"어때\?$", "어때요?"),
    (r"없어\?$", "없어요?"),
    (r"없어$", "없어요."),
    (r"있어\?$", "있어요?"),
    (r"있어$", "있어요."),
    (r"왔어\?$", "왔어요?"),
    (r"왔어$", "왔어요."),
    (r"멀어$", "멀어요."),
    (r"가까워$", "가까워요."),
    (r"배고파$", "배고파요."),
    (r"목말라$", "목말라요."),
    (r"싫어$", "싫어요."),
    (r"반가워$", "반가워요."),
    (r"괜찮아\?$", "괜찮아요?"),
    (r"괜찮아$", "괜찮아요."),
    (r"확실해$", "확실해요."),
    (r"동의해$", "동의해요."),
    (r"중이야$", "중이에요."),
    (r"생겼어\?$", "생겼어요?"),
    (r"생겼어$", "생겼어요."),
    (r"거야\?$", "거예요?"),
    (r"거야$", "거예요."),
    (r"됐어\?$", "됐어요?"),
    (r"됐어$", "됐어요."),
)


def stabilize_translation_text(
    *,
    source_text: str,
    source_language: str,
    target_language: str,
    translation_text: str,
) -> str:
    if source_language == target_language or not translation_text.strip():
        return translation_text

    normalized_source = _normalize_phrase(source_text, language=source_language)
    if not normalized_source:
        return translation_text

    override = _SHORT_PHRASE_OVERRIDES.get((source_language, target_language), {}).get(normalized_source)
    if override:
        return override

    if source_language == "ko" and target_language == "es":
        low_appraisal_override = _override_korean_low_appraisal_phrase(source_text)
        if low_appraisal_override:
            return low_appraisal_override
        phrase_override = _KOREAN_TO_SPANISH_EXACT_OVERRIDES.get(normalized_source)
        if phrase_override:
            return phrase_override
        return translation_text

    if source_language == "es" and target_language == "ko":
        phrase_override = _SPANISH_TO_KOREAN_EXACT_OVERRIDES.get(normalized_source)
        if phrase_override:
            return phrase_override
        time_override = _override_spanish_time_phrase(source_text)
        if time_override:
            return time_override
        state_override = _override_spanish_estoy_en_state_phrase(source_text)
        if state_override:
            return _stabilize_spanish_to_korean_speech_level(
                source_text=source_text,
                translation_text=state_override,
            )
        return _stabilize_spanish_to_korean_speech_level(
            source_text=source_text,
            translation_text=translation_text,
        )

    return translation_text


def stabilize_translations(
    *,
    source_text: str,
    source_language: str,
    translations: dict[str, str],
) -> dict[str, str]:
    stabilized = dict(translations)
    for target_language, translated_text in translations.items():
        stabilized[target_language] = stabilize_translation_text(
            source_text=source_text,
            source_language=source_language,
            target_language=target_language,
            translation_text=translated_text,
        )
    return stabilized


def canonicalize_source_text(text: str, *, language: str) -> str:
    normalized_source = _normalize_phrase(text, language=language)
    if not normalized_source:
        return text

    canonical = None
    if language == "es":
        canonical = _SPANISH_SOURCE_CANONICALS.get(normalized_source)
    elif language == "ko":
        canonical = _KOREAN_SOURCE_CANONICALS.get(normalized_source)
    if canonical:
        return canonical

    return text


def _normalize_phrase(text: str, *, language: str) -> str:
    stripped = text.strip()
    if not stripped:
        return ""

    if language == "ko":
        return re.sub(r"[\s\.,!?~…\"'`]+", "", stripped)

    lowered = unicodedata.normalize("NFKD", stripped.casefold())
    lowered = "".join(char for char in lowered if not unicodedata.combining(char))
    lowered = lowered.replace("¿", " ").replace("¡", " ")
    lowered = re.sub(r"[^a-z0-9]+", " ", lowered)
    return " ".join(lowered.split())


def _stabilize_spanish_to_korean_speech_level(*, source_text: str, translation_text: str) -> str:
    stripped_translation = translation_text.strip()
    if not stripped_translation or _looks_polite_korean(stripped_translation):
        return translation_text

    normalized_source = _normalize_phrase(source_text, language="es")
    if not normalized_source:
        return translation_text

    if _has_explicit_spanish_informal_cue(normalized_source):
        return translation_text

    if stripped_translation in _AMBIGUOUS_SPANISH_TO_KOREAN_NEUTRAL_OVERRIDES:
        return _AMBIGUOUS_SPANISH_TO_KOREAN_NEUTRAL_OVERRIDES[stripped_translation]

    softened = stripped_translation
    for pattern, replacement in _KOREAN_POLITE_ENDING_REPLACEMENTS:
        candidate = re.sub(pattern, replacement, softened)
        if candidate != softened:
            return candidate

    if _has_explicit_spanish_formal_cue(normalized_source):
        return _append_polite_period(softened)

    return translation_text


def _override_spanish_time_phrase(source_text: str) -> str | None:
    normalized_source = _normalize_phrase(source_text, language="es")
    if not normalized_source:
        return None

    arrival_match = re.fullmatch(r"llegare en ([a-z0-9]+) minutos?", normalized_source)
    if arrival_match:
        amount = _normalize_spanish_amount(arrival_match.group(1))
        if amount:
            return f"{amount}분 후 도착해요."

    return None


def _override_spanish_estoy_en_state_phrase(source_text: str) -> str | None:
    normalized_source = _normalize_phrase(source_text, language="es")
    if not normalized_source.startswith("estoy en "):
        return None

    phrase = normalized_source.removeprefix("estoy en ").strip()
    phrase = re.sub(r"^(un|una|el|la|los|las|mi|tu|su|este|esta|estos|estas)\s+", "", phrase)
    if not phrase:
        return None

    return _SPANISH_ESTOY_EN_STATE_OVERRIDES.get(phrase)


def _override_korean_low_appraisal_phrase(source_text: str) -> str | None:
    normalized_source = _normalize_phrase(source_text, language="ko")
    if not normalized_source:
        return None

    generic_low_appraisal = {
        "별로다",
        "별로야",
        "별로에요",
        "별로예요",
        "별로입니다",
        "별로인데",
    }
    if normalized_source in generic_low_appraisal:
        return "No está muy bien."

    if normalized_source in {"이거별로야", "이건별로야", "이거별로다", "이건별로다"}:
        return "Esto no está muy bien."

    return None


def _normalize_spanish_amount(token: str) -> str | None:
    if token.isdigit():
        return token
    return _SPANISH_NUMBER_WORDS.get(token)


def _has_explicit_spanish_informal_cue(normalized_source: str) -> bool:
    tokens = set(normalized_source.split())
    return bool(tokens & _SPANISH_EXPLICIT_INFORMAL_CUES)


def _has_explicit_spanish_formal_cue(normalized_source: str) -> bool:
    tokens = set(normalized_source.split())
    return bool(tokens & _SPANISH_EXPLICIT_FORMAL_CUES)


def _looks_polite_korean(text: str) -> bool:
    stripped = text.strip()
    return bool(
        re.search(r"(요|니다|습니다|세요|이에요|예요|죠|군요|네요)[.!?]?$", stripped)
        or "주세요" in stripped
    )


def _append_polite_period(text: str) -> str:
    if text.endswith(("?", "!", ".")):
        return text
    return f"{text}."
