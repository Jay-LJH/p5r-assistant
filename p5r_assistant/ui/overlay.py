from __future__ import annotations

from p5r_assistant.match.matcher import MatchResult


def format_recommendation(result: MatchResult) -> str:
    recommendation = result.recommendation
    if recommendation is None:
        return format_candidates(result)
    choice = recommendation.choice
    return (
        f"P5R Assistant\n\n推荐：第 {choice.index} 项 {choice.text}\n\n"
        f"好感：{choice.points}\n"
        f"{recommendation.confidant.name} / Rank {recommendation.event.rank_to or '?'} / 置信度 {result.score:.0%}"
    )


def format_candidates(result: MatchResult) -> str:
    lines = ["匹配不确定"]
    for index, candidate in enumerate(result.candidates, start=1):
        choice = candidate.choice
        lines.append(
            f"{index}. {candidate.confidant.name} Rank {candidate.event.rank_to or '?'} "
            f"第 {choice.index} 项 / +{choice.points} / {candidate.score:.0%}"
        )
    return "\n".join(lines)


class ConsoleOverlay:
    def show_recommendation(self, result: MatchResult) -> None:
        print(format_recommendation(result))

    def show_candidates(self, result: MatchResult) -> None:
        print(format_candidates(result))

    def show_error(self, message: str) -> None:
        print(f"P5R Assistant error: {message}")


class QtOverlay:
    def __init__(self, timeout_seconds: int = 5) -> None:
        try:
            from PySide6.QtCore import Qt, QTimer
            from PySide6.QtWidgets import QLabel
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("PySide6 is not installed") from exc

        self._timer_cls = QTimer
        self.timeout_ms = timeout_seconds * 1000
        self.widget = QLabel()
        self.widget.setWindowFlags(Qt.WindowType.Tool | Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.widget.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.widget.setWordWrap(True)
        self.widget.setStyleSheet(
            "QLabel { background: rgba(20, 20, 24, 220); color: white; "
            "padding: 14px; border-radius: 6px; font-size: 16px; }"
        )

    def show_recommendation(self, result: MatchResult) -> None:
        self._show_text(format_recommendation(result))

    def show_candidates(self, result: MatchResult) -> None:
        self._show_text(format_candidates(result))

    def show_error(self, message: str) -> None:
        self._show_text(f"P5R Assistant error:\n{message}")

    def _show_text(self, text: str) -> None:
        self.widget.setText(text)
        self.widget.adjustSize()
        self.widget.move(40, 40)
        self.widget.show()
        self._timer_cls.singleShot(self.timeout_ms, self.widget.hide)
