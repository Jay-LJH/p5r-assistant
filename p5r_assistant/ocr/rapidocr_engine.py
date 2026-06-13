from __future__ import annotations

from p5r_assistant.ocr.engine import OcrLine


class RapidOcrEngine:
    def __init__(self) -> None:
        try:
            from rapidocr_onnxruntime import RapidOCR
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("rapidocr-onnxruntime is not installed") from exc
        self._engine = RapidOCR()

    def recognize(self, image) -> list[OcrLine]:
        result, _ = self._engine(image)
        lines: list[OcrLine] = []
        for box, text, confidence in result or []:
            xs = [int(point[0]) for point in box]
            ys = [int(point[1]) for point in box]
            lines.append(OcrLine(text=text, confidence=float(confidence), box=(min(xs), min(ys), max(xs), max(ys))))
        return lines
