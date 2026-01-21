import re
import difflib


def normalize_location(value: str) -> str:
    cleaned = value.lower()
    cleaned = cleaned.replace(",", " ")
    cleaned = re.sub(r"[^a-z0-9\s]", " ", cleaned)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def fallback_similarity(a: str, b: str) -> float:
    return difflib.SequenceMatcher(None, a, b).ratio()
