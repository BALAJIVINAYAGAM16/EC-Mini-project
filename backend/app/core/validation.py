import html
import re


CONTROL_CHARS = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")


def sanitize_text(value: str) -> str:
    cleaned = CONTROL_CHARS.sub("", value).strip()
    return html.escape(cleaned, quote=False)


def sanitize_optional_text(value: str | None) -> str | None:
    if value is None:
        return value
    return sanitize_text(value)
