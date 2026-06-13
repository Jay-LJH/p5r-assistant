from p5r_assistant.desktop import DesktopController


class FakeService:
    def __init__(self):
        self.calls = 0

    def recognize_once(self):
        self.calls += 1


class FakeOverlay:
    def __init__(self):
        self.errors = []

    def show_error(self, message):
        self.errors.append(message)


def test_desktop_controller_hotkey_triggers_recognition_when_enabled():
    service = FakeService()
    controller = DesktopController(service=service, overlay=FakeOverlay())

    controller.trigger_recognition()

    assert service.calls == 1


def test_desktop_controller_does_not_recognize_when_paused():
    service = FakeService()
    controller = DesktopController(service=service, overlay=FakeOverlay())

    controller.set_enabled(False)
    controller.trigger_recognition()

    assert service.calls == 0


def test_desktop_controller_reports_recognition_errors():
    class FailingService:
        def recognize_once(self):
            raise RuntimeError("no window")

    overlay = FakeOverlay()
    controller = DesktopController(service=FailingService(), overlay=overlay)

    controller.trigger_recognition()

    assert overlay.errors == ["no window"]
