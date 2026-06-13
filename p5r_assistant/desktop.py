from __future__ import annotations

from p5r_assistant.recognition import OverlayPresenter, RecognitionService


class DesktopController:
    def __init__(self, service: RecognitionService, overlay: OverlayPresenter) -> None:
        self.service = service
        self.overlay = overlay
        self.enabled = True

    def set_enabled(self, enabled: bool) -> None:
        self.enabled = enabled

    def trigger_recognition(self) -> None:
        if not self.enabled:
            return
        try:
            self.service.recognize_once()
        except Exception as exc:
            self.overlay.show_error(str(exc))
