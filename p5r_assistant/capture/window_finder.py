from __future__ import annotations

import ctypes
from ctypes import wintypes
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

_DPI_AWARENESS_SET = False


def is_p5r_window_title(title: str) -> bool:
    normalized = (title or "").strip()
    if normalized in _EXACT_TITLES:
        return True
    lowered = normalized.lower()
    if any(excluded in lowered for excluded in _EXCLUDED_TITLE_PARTS):
        return False
    return lowered == "p5r"


def ensure_process_dpi_aware() -> None:
    global _DPI_AWARENESS_SET
    if _DPI_AWARENESS_SET:
        return

    try:
        import ctypes

        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass
    _DPI_AWARENESS_SET = True


def _get_extended_frame_bounds(hwnd: int) -> tuple[int, int, int, int] | None:
    try:
        rect = wintypes.RECT()
        result = ctypes.windll.dwmapi.DwmGetWindowAttribute(
            hwnd,
            9,  # DWMWA_EXTENDED_FRAME_BOUNDS
            ctypes.byref(rect),
            ctypes.sizeof(rect),
        )
    except Exception:
        return None
    if result != 0:
        return None
    return rect.left, rect.top, rect.right, rect.bottom


def _get_virtual_screen_bounds() -> tuple[int, int, int, int]:
    try:
        user32 = ctypes.windll.user32
        left = user32.GetSystemMetrics(76)  # SM_XVIRTUALSCREEN
        top = user32.GetSystemMetrics(77)  # SM_YVIRTUALSCREEN
        width = user32.GetSystemMetrics(78)  # SM_CXVIRTUALSCREEN
        height = user32.GetSystemMetrics(79)  # SM_CYVIRTUALSCREEN
        if width > 0 and height > 0:
            return left, top, left + width, top + height
        width = user32.GetSystemMetrics(0)  # SM_CXSCREEN
        height = user32.GetSystemMetrics(1)  # SM_CYSCREEN
        return 0, 0, width, height
    except Exception:
        return 0, 0, 0, 0


def _is_usable_window(win32gui, hwnd: int) -> bool:
    is_visible = getattr(win32gui, "IsWindowVisible", None)
    if is_visible is not None and not is_visible(hwnd):
        return False
    is_iconic = getattr(win32gui, "IsIconic", None)
    if is_iconic is not None and is_iconic(hwnd):
        return False
    return True


def _valid_rect(rect: tuple[int, int, int, int]) -> bool:
    left, top, right, bottom = rect
    return right > left and bottom > top


def _get_window_bounds(win32gui, hwnd: int) -> tuple[int, int, int, int] | None:
    rect = _get_extended_frame_bounds(hwnd)
    if rect is not None and _valid_rect(rect):
        return rect
    try:
        rect = win32gui.GetWindowRect(hwnd)
    except Exception:
        return None
    if _valid_rect(rect):
        return rect
    return None


def _window_info_from_rect(hwnd: int, title: str, rect: tuple[int, int, int, int]) -> WindowInfo:
    left, top, right, bottom = rect
    return WindowInfo(hwnd, title, left, top, right - left, bottom - top)


def _get_foreground_window(win32gui) -> int:
    get_foreground_window = getattr(win32gui, "GetForegroundWindow", None)
    if get_foreground_window is None:
        return 0
    try:
        return int(get_foreground_window())
    except Exception:
        return 0


def _make_window_info(win32gui, hwnd: int, *, allow_fullscreen_fallback: bool = False) -> WindowInfo | None:
    title = win32gui.GetWindowText(hwnd)
    if not title or not is_p5r_window_title(title):
        return None
    if not _is_usable_window(win32gui, hwnd):
        return None

    rect = _get_window_bounds(win32gui, hwnd)
    if rect is None and allow_fullscreen_fallback:
        rect = _get_virtual_screen_bounds()
    if rect is None or not _valid_rect(rect):
        return None
    return _window_info_from_rect(hwnd, title, rect)


def find_p5r_window() -> WindowInfo:
    ensure_process_dpi_aware()
    try:
        import win32gui
    except ImportError as exc:  # pragma: no cover
        raise WindowNotFoundError("pywin32 is not installed; cannot locate the game window") from exc

    matches: list[WindowInfo] = []
    foreground_hwnd = _get_foreground_window(win32gui)

    def callback(hwnd, _):
        found = _make_window_info(win32gui, hwnd)
        if found is not None:
            matches.append(found)

    win32gui.EnumWindows(callback, None)
    for match in matches:
        if match.handle == foreground_hwnd:
            return match
    if not matches:
        if foreground_hwnd:
            foreground = _make_window_info(win32gui, foreground_hwnd, allow_fullscreen_fallback=True)
            if foreground is not None:
                return foreground
        raise WindowNotFoundError("P5R window was not found")
    return matches[0]
