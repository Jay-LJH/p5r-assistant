from p5r_assistant.ui import overlay


class _FakeWidget:
    def winId(self):
        return 12345


def test_raise_widget_to_topmost_uses_native_topmost_without_activation():
    calls = []

    def fake_set_window_pos(hwnd, insert_after, x, y, cx, cy, flags):
        calls.append((hwnd, insert_after, x, y, cx, cy, flags))
        return 1

    overlay.raise_widget_to_topmost(_FakeWidget(), set_window_pos=fake_set_window_pos)

    assert calls == [
        (
            12345,
            overlay.HWND_TOPMOST,
            0,
            0,
            0,
            0,
            overlay.SWP_NOMOVE | overlay.SWP_NOSIZE | overlay.SWP_NOACTIVATE,
        )
    ]


class _FakeTimer:
    @staticmethod
    def singleShot(timeout_ms, callback):
        callback()


class _FakeOverlayWidget:
    def __init__(self):
        self.events = []
        self.text = None
        self._width = 240

    def setText(self, text):
        self.events.append("setText")
        self.text = text

    def adjustSize(self):
        self.events.append("adjustSize")

    def move(self, x, y):
        self.events.append(("move", x, y))

    def width(self):
        return self._width

    def screen(self):
        return _FakeScreen()

    def show(self):
        self.events.append("show")

    def hide(self):
        self.events.append("hide")


class _FakeRect:
    def right(self):
        return 1920

    def top(self):
        return 0


class _FakeScreen:
    def availableGeometry(self):
        return _FakeRect()


def test_show_text_raises_overlay_after_show(monkeypatch):
    widget = _FakeOverlayWidget()
    raised = []

    def fake_raise_widget_to_topmost(seen_widget):
        raised.append(seen_widget)
        seen_widget.events.append("raise")

    monkeypatch.setattr(overlay, "raise_widget_to_topmost", fake_raise_widget_to_topmost)
    qt_overlay = overlay.QtOverlay.__new__(overlay.QtOverlay)
    qt_overlay.widget = widget
    qt_overlay.timeout_ms = 5000
    qt_overlay._timer_cls = _FakeTimer

    qt_overlay._show_text("help")

    assert widget.text == "help"
    assert raised == [widget]
    assert widget.events == ["setText", "adjustSize", ("move", 1656, 24), "show", "raise", "hide"]


def test_overlay_style_has_readable_background():
    assert "background: rgba(8, 10, 14, 245)" in overlay.OVERLAY_STYLESHEET
    assert "border: 1px solid rgba(255, 255, 255, 180)" in overlay.OVERLAY_STYLESHEET
