import threading

import pytest


def test_qt_recognition_dispatcher_queues_worker_thread_trigger_on_qt_event_loop():
    pytest.importorskip("PySide6")
    from PySide6.QtCore import QCoreApplication

    from p5r_assistant.ui.tray import QtRecognitionDispatcher

    app = QCoreApplication.instance() or QCoreApplication([])
    calls = []
    dispatcher = QtRecognitionDispatcher(lambda: calls.append("hit"))

    thread = threading.Thread(target=dispatcher.trigger)
    thread.start()
    thread.join(timeout=1)

    assert calls == []

    app.processEvents()

    assert calls == ["hit"]
