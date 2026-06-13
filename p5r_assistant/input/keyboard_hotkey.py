from __future__ import annotations

from collections.abc import Callable


class KeyboardHotkey:
    def __init__(self, hotkey: str, callback: Callable[[], None]) -> None:
        self.hotkey = hotkey
        self.callback = callback
        self._keyboard = None

    def start(self) -> None:
        try:
            import keyboard
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("keyboard package is not installed") from exc
        self._keyboard = keyboard
        keyboard.add_hotkey(self.hotkey, self.callback)

    def stop(self) -> None:
        if self._keyboard is not None:
            self._keyboard.remove_hotkey(self.hotkey)
