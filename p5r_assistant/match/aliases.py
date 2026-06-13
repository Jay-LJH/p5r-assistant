from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from p5r_assistant.config.settings import _atomic_write_json
from p5r_assistant.match.normalize import normalize_text


@dataclass(slots=True)
class AliasEntry:
    ocr_text: str
    canonical_text: str
    choice_id: str
    created_at: str


class AliasStore:
    def __init__(self, entries: list[AliasEntry] | None = None) -> None:
        self.entries = entries or []
        self._by_ocr = {normalize_text(entry.ocr_text): entry for entry in self.entries}

    @classmethod
    def empty(cls) -> "AliasStore":
        return cls([])

    @classmethod
    def load(cls, path: Path) -> "AliasStore":
        if not path.exists():
            _atomic_write_json(path, [])
            return cls.empty()
        data = json.loads(path.read_text(encoding="utf-8"))
        return cls([AliasEntry(**entry) for entry in data])

    def save(self, path: Path) -> None:
        _atomic_write_json(path, [asdict(entry) for entry in self.entries])

    def resolve(self, ocr_text: str) -> str | None:
        entry = self._by_ocr.get(normalize_text(ocr_text))
        return entry.canonical_text if entry else None
