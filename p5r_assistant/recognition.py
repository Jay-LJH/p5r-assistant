from __future__ import annotations

from typing import Protocol

from p5r_assistant.guide.schema import Guide
from p5r_assistant.match.aliases import AliasStore
from p5r_assistant.match.matcher import MatchResult, Matcher
from p5r_assistant.ocr.engine import OcrEngine, group_option_lines


class ChoiceCapture(Protocol):
    def capture_choice_region(self):
        ...


class OverlayPresenter(Protocol):
    def show_recommendation(self, result: MatchResult) -> None:
        ...

    def show_candidates(self, result: MatchResult) -> None:
        ...

    def show_error(self, message: str) -> None:
        ...


class RecognitionService:
    def __init__(
        self,
        capture: ChoiceCapture,
        ocr: OcrEngine,
        guide: Guide,
        aliases: AliasStore,
        overlay: OverlayPresenter,
    ) -> None:
        self.capture = capture
        self.ocr = ocr
        self.matcher = Matcher(guide, aliases)
        self.overlay = overlay

    def recognize_once(self) -> MatchResult:
        try:
            image = self.capture.capture_choice_region()
            lines = self.ocr.recognize(image)
            choices = group_option_lines(lines)
            result = self.matcher.match(choices)
        except Exception as exc:
            self.overlay.show_error(str(exc))
            raise

        if result.confident or result.uncertain:
            self.overlay.show_recommendation(result)
        else:
            self.overlay.show_candidates(result)
        return result
