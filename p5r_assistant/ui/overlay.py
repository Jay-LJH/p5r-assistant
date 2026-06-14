from __future__ import annotations

import html
import re

from p5r_assistant.match.matcher import MatchResult

HWND_TOPMOST = -1
SWP_NOSIZE = 0x0001
SWP_NOMOVE = 0x0002
SWP_NOACTIVATE = 0x0010
OVERLAY_MARGIN = 24
OVERLAY_STYLESHEET = (
    "QLabel { background: rgba(8, 10, 14, 245); color: white; "
    "border: 1px solid rgba(255, 255, 255, 180); "
    "padding: 14px; border-radius: 6px; font-size: 16px; }"
)
ROMANCE_CONDITION_RE = re.compile(r"([（(][^）)]*(?:恋人条件|戀人條件)[^）)]*[）)])")
RICH_TEXT_STYLE = (
    "<style>"
    ".romance-condition { color: #ff5c8a; font-family: 'KaiTi', 'Microsoft YaHei UI', sans-serif; "
    "font-size: 18px; font-style: italic; font-weight: 800; }"
    "</style>"
)


def raise_widget_to_topmost(widget, set_window_pos=None) -> None:
    if set_window_pos is None:
        try:
            import ctypes

            set_window_pos = ctypes.windll.user32.SetWindowPos
        except Exception:
            return

    try:
        hwnd = int(widget.winId())
        set_window_pos(
            hwnd,
            HWND_TOPMOST,
            0,
            0,
            0,
            0,
            SWP_NOMOVE | SWP_NOSIZE | SWP_NOACTIVATE,
        )
    except Exception:
        return


def move_widget_to_top_right(widget, margin: int = OVERLAY_MARGIN) -> None:
    try:
        screen = widget.screen()
        geometry = screen.availableGeometry()
        x = geometry.right() - widget.width() - margin
        y = geometry.top() + margin
    except Exception:
        x = margin
        y = margin
    widget.move(x, y)


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


def format_recommendation_rich_text(result: MatchResult) -> str:
    recommendation = result.recommendation
    if recommendation is None:
        return _plain_text_to_rich_text(format_candidates(result))
    choice = recommendation.choice
    return (
        f"<html><head>{RICH_TEXT_STYLE}</head><body>"
        f"{html.escape('P5R Assistant')}<br><br>"
        f"{html.escape('鎺ㄨ崘锛氱 ')}{choice.index}{html.escape(' 椤?')}"
        f"{_emphasize_romance_condition(choice.text)}<br><br>"
        f"{html.escape('濂芥劅锛?')}{choice.points}<br>"
        f"{html.escape(recommendation.confidant.name)} / Rank {recommendation.event.rank_to or '?'} / "
        f"{html.escape('缃俊搴?')}{result.score:.0%}"
        f"</body></html>"
    )


def _plain_text_to_rich_text(text: str) -> str:
    return f"<html><body>{html.escape(text).replace(chr(10), '<br>')}</body></html>"


def _emphasize_romance_condition(text: str) -> str:
    parts = []
    last_index = 0
    for match in ROMANCE_CONDITION_RE.finditer(text):
        parts.append(html.escape(text[last_index : match.start()]))
        parts.append(f'<span class="romance-condition">{html.escape(match.group(1))}</span>')
        last_index = match.end()
    parts.append(html.escape(text[last_index:]))
    return "".join(parts)


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
        self.widget.setStyleSheet(OVERLAY_STYLESHEET)

    def show_recommendation(self, result: MatchResult) -> None:
        self._show_text(format_recommendation_rich_text(result))

    def show_candidates(self, result: MatchResult) -> None:
        self._show_text(format_candidates(result))

    def show_error(self, message: str) -> None:
        self._show_text(f"P5R Assistant error:\n{message}")

    def _show_text(self, text: str) -> None:
        self.widget.setText(text)
        self.widget.adjustSize()
        move_widget_to_top_right(self.widget)
        self.widget.show()
        raise_widget_to_topmost(self.widget)
        self._timer_cls.singleShot(self.timeout_ms, self.widget.hide)
