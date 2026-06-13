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


def find_p5r_window(title_keywords: tuple[str, ...] = ("Persona 5 Royal", "P5R")) -> WindowInfo:
    try:
        import win32gui
    except ImportError as exc:  # pragma: no cover
        raise WindowNotFoundError("pywin32 is not installed; cannot locate the game window") from exc

    matches: list[WindowInfo] = []

    def callback(hwnd, _):
        title = win32gui.GetWindowText(hwnd)
        if title and any(keyword.lower() in title.lower() for keyword in title_keywords):
            left, top, right, bottom = win32gui.GetWindowRect(hwnd)
            matches.append(WindowInfo(hwnd, title, left, top, right - left, bottom - top))

    win32gui.EnumWindows(callback, None)
    if not matches:
        raise WindowNotFoundError("P5R window was not found")
    return matches[0]
