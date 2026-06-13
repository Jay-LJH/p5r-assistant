from __future__ import annotations

from dataclasses import dataclass

from p5r_assistant.config.settings import load_settings
from p5r_assistant.desktop import DesktopController
from p5r_assistant.input.gamepad import GamepadComboListener
from p5r_assistant.input.keyboard_hotkey import KeyboardHotkey
from p5r_assistant.runtime import LazyRecognitionService, RuntimePaths
from p5r_assistant.ui.overlay import ConsoleOverlay, QtOverlay


@dataclass(slots=True)
class DesktopAppConfig:
    enable_keyboard: bool = True
    enable_gamepad: bool = True


class QtRecognitionDispatcher:
    def __init__(self, callback):
        try:
            from PySide6.QtCore import QObject, Signal, Slot
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError("PySide6 is not installed") from exc

        class _Dispatcher(QObject):
            triggered = Signal()

            def __init__(self, callback):
                super().__init__()
                self._callback = callback
                self.triggered.connect(self._run)

            @Slot()
            def _run(self):
                self._callback()

        self._dispatcher = _Dispatcher(callback)

    def trigger(self) -> None:
        self._dispatcher.triggered.emit()


def run_app(paths: RuntimePaths | None = None, config: DesktopAppConfig | None = None) -> int:
    paths = paths or RuntimePaths()
    config = config or DesktopAppConfig()
    try:
        from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon
        from PySide6.QtGui import QAction, QIcon
    except ImportError:
        overlay = ConsoleOverlay()
        service = LazyRecognitionService(paths, overlay=overlay)
        controller = DesktopController(service, overlay)
        _start_listeners(paths, config, controller.trigger_recognition, overlay)
        print("P5R Assistant console mode. Press configured hotkey if available; install p5r-assistant[ui] for tray UI.")
        return 0

    app = QApplication([])
    settings = load_settings(paths.settings_path)
    overlay = QtOverlay(settings.overlay_timeout_seconds)
    service = LazyRecognitionService(paths, overlay=overlay)
    controller = DesktopController(service, overlay)
    dispatcher = QtRecognitionDispatcher(controller.trigger_recognition)
    listeners = _start_listeners(paths, config, dispatcher.trigger, overlay)
    tray = QSystemTrayIcon(QIcon())
    tray.setToolTip("P5R Assistant")
    menu = QMenu()
    recognize_action = QAction("Recognize now")
    recognize_action.triggered.connect(controller.trigger_recognition)
    menu.addAction(recognize_action)
    pause_action = QAction("Pause")
    pause_action.setCheckable(True)
    pause_action.triggered.connect(lambda checked: controller.set_enabled(not checked))
    menu.addAction(pause_action)
    exit_action = QAction("Exit")
    exit_action.triggered.connect(app.quit)
    menu.addAction(exit_action)
    tray.setContextMenu(menu)
    tray.show()
    try:
        return app.exec()
    finally:
        for listener in listeners:
            listener.stop()


def _start_listeners(paths: RuntimePaths, config: DesktopAppConfig, trigger_recognition, overlay) -> list:
    settings = load_settings(paths.settings_path)
    listeners = []
    if config.enable_keyboard:
        listeners.append(KeyboardHotkey(settings.keyboard_hotkey, trigger_recognition))
    if config.enable_gamepad:
        listeners.append(GamepadComboListener(settings.controller_combo, trigger_recognition))

    for listener in listeners:
        try:
            listener.start()
        except Exception as exc:
            print(f"P5R Assistant listener error: {exc}")
            overlay.show_error(str(exc))
    return listeners
