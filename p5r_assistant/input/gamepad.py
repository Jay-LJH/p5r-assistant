from __future__ import annotations

from collections.abc import Callable
import threading
import time


_BUTTON_INDEX = {
    "A": 0,
    "B": 1,
    "X": 2,
    "Y": 3,
    "LB": 4,
    "RB": 5,
}


class GamepadComboListener:
    def __init__(self, combo: list[str], callback: Callable[[], None], poll_interval: float = 0.05) -> None:
        self.combo = combo
        self.callback = callback
        self.poll_interval = poll_interval
        self._pressed = False
        self._running = False
        self._thread: threading.Thread | None = None

    def start(self) -> None:
        try:
            import pygame
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("pygame is not installed") from exc
        pygame.init()
        pygame.joystick.init()
        if pygame.joystick.get_count() < 1:
            raise RuntimeError("no gamepad detected")
        joystick = pygame.joystick.Joystick(0)
        joystick.init()
        self._running = True
        self._thread = threading.Thread(target=self._poll_loop, args=(pygame, joystick), daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=1)

    def handle_buttons(self, pressed_buttons: set[str]) -> None:
        combo_pressed = set(self.combo).issubset(pressed_buttons)
        if combo_pressed and not self._pressed:
            self.callback()
        self._pressed = combo_pressed

    def _poll_loop(self, pygame, joystick) -> None:  # pragma: no cover - hardware loop
        while self._running:
            pygame.event.pump()
            pressed = {
                name
                for name, index in _BUTTON_INDEX.items()
                if index < joystick.get_numbuttons() and joystick.get_button(index)
            }
            self.handle_buttons(pressed)
            time.sleep(self.poll_interval)
