from __future__ import annotations

from dataclasses import dataclass


class WindowNotFoundError(RuntimeError):
    pass


@dataclass(slots=True)
class WindowInfo:
    handle: int
    title: str
    left: int
    top: int
    width: int
    height: int


_EXACT_TITLES = {
    "Persona 5 Royal",
    "女神异闻录5皇家版",
    "\u6fc2\u5d07\ue6a3\u5bee\u509e\u6908\u8930?\u9428\u56e7\ue18d\u9417?",
}

_EXCLUDED_TITLE_PARTS = (
    "visual studio code",
    "codex",
    "p5r assistant",
)


def is_p5r_window_title(title: str) -> bool:
    normalized = (title or "").strip()
    if normalized in _EXACT_TITLES:
        return True
    lowered = normalized.lower()
    if any(excluded in lowered for excluded in _EXCLUDED_TITLE_PARTS):
        return False
    return lowered == "p5r"


def find_p5r_window() -> WindowInfo:
    try:
        import win32gui
    except ImportError as exc:  # pragma: no cover
        raise WindowNotFoundError("pywin32 is not installed; cannot locate the game window") from exc

    matches: list[WindowInfo] = []

    def callback(hwnd, _):
        title = win32gui.GetWindowText(hwnd)
        if title and is_p5r_window_title(title):
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            matches.append(WindowInfo(hwnd, title, left, top, right - left, bottom - top))

    win32gui.EnumWindows(callback, None)
    if not matches:
        raise WindowNotFoundError("P5R window was not found")
    return matches[0]
