from __future__ import annotations


def open_settings_window() -> int:
    try:
        from PySide6.QtWidgets import QApplication, QLabel, QTabWidget, QVBoxLayout, QWidget
    except ImportError:
        print("PySide6 is not installed; settings UI is unavailable.")
        return 1

    app = QApplication.instance() or QApplication([])
    window = QWidget()
    window.setWindowTitle("P5R Assistant Settings")
    layout = QVBoxLayout(window)
    tabs = QTabWidget()
    for name in ["Hotkeys", "Recognition", "Guide", "Display"]:
        tabs.addTab(QLabel(f"{name} settings"), name)
    layout.addWidget(tabs)
    window.show()
    return app.exec()
