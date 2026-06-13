from __future__ import annotations

from p5r_assistant.capture.window_finder import WindowInfo


class ScreenshotError(RuntimeError):
    pass


def screenshot_window(window: WindowInfo):
    try:
        import mss
        from PIL import Image
    except ImportError as exc:  # pragma: no cover
        raise ScreenshotError("mss and Pillow are required for screenshots") from exc

    monitor = {"left": window.left, "top": window.top, "width": window.width, "height": window.height}
    with mss.mss() as screen:
        shot = screen.grab(monitor)
    return Image.frombytes("RGB", shot.size, shot.rgb)
