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
        _start_listeners(paths, config, controller, overlay)
        print("P5R Assistant console mode. Press configured hotkey if available; install p5r-assistant[ui] for tray UI.")
        return 0

    app = QApplication([])
    settings = load_settings(paths.settings_path)
    overlay = QtOverlay(settings.overlay_timeout_seconds)
    service = LazyRecognitionService(paths, overlay=overlay)
    controller = DesktopController(service, overlay)
    listeners = _start_listeners(paths, config, controller, overlay)
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


def _start_listeners(paths: RuntimePaths, config: DesktopAppConfig, controller: DesktopController, overlay) -> list:
    settings = load_settings(paths.settings_path)
    listeners = []
    if config.enable_keyboard:
        listeners.append(KeyboardHotkey(settings.keyboard_hotkey, controller.trigger_recognition))
    if config.enable_gamepad:
        listeners.append(GamepadComboListener(settings.controller_combo, controller.trigger_recognition))

    for listener in listeners:
        try:
            listener.start()
        except Exception as exc:
            overlay.show_error(str(exc))
    return listeners
