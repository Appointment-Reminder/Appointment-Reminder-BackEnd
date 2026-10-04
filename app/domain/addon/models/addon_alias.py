from typing import Optional


def normalize_alias(alias: Optional[str]) -> str:
    """The comparable form of an Alias: non-breaking spaces are plain spaces, surrounding whitespace is dropped."""
    return (alias or "").replace(" ", " ").strip()
