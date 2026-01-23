import re


DANGEROUS_CHARS = re.compile(r"[<>\\\"'`;]")
ALLOWED_SANITIZE = re.compile(r"[^a-zA-Z0-9 ]+")


def validate_text(text: str | None, max_length: int = 500) -> bool:
    if not text:
        return False
    cleaned = text.strip()
    if not cleaned:
        return False
    if len(cleaned) > max_length:
        return False
    if DANGEROUS_CHARS.search(cleaned):
        return False
    return True


def validate_positive_number(value: str | int | float) -> bool:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return False
    return number > 0


def sanitize_string(text: str) -> str:
    cleaned = ALLOWED_SANITIZE.sub("", text or "")
    return cleaned.lower().strip()
