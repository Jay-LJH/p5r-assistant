from __future__ import annotations

import re
import unicodedata

_PUNCTUATION = {
    "？": "?",
    "！": "!",
    "。": ".",
    "，": ",",
    "：": ":",
    "；": ";",
    "“": '"',
    "”": '"',
    "‘": "'",
    "’": "'",
    "…": "...",
    "—": "-",
    "～": "~",
}

_NOISE = str.maketrans({"|": "", "¦": "", "丨": ""})


def normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKC", text or "")
    for source, target in _PUNCTUATION.items():
        normalized = normalized.replace(source, target)
    normalized = normalized.translate(_NOISE)
    normalized = re.sub(r"\s+", "", normalized)
    normalized = re.sub(r"\.{4,}", "...", normalized)
    return normalized
