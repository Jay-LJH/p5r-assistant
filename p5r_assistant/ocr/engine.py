from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(slots=True)
class OcrLine:
    text: str
    confidence: float
    box: tuple[int, int, int, int]


class OcrEngine(Protocol):
    def recognize(self, image) -> list[OcrLine]:
        ...


def group_option_lines(lines: list[OcrLine], min_confidence: float = 0.4) -> list[str]:
    usable = [line for line in lines if line.confidence >= min_confidence and line.text.strip()]
    usable.sort(key=lambda line: (line.box[1], line.box[0]))
    return [line.text.strip() for line in usable]
