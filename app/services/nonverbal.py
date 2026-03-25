import unicodedata


def is_nonverbal_text(text: str) -> bool:
    stripped = text.strip()
    if not stripped:
        return False

    has_alnum = any(char.isalnum() for char in stripped)
    if has_alnum:
        return False

    return any(unicodedata.category(char)[0] in {"S", "P", "M"} for char in stripped if not char.isspace())
