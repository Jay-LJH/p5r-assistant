from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from p5r_assistant.capture.choice_region import P5RChoiceRegionCapture
from p5r_assistant.config.settings import load_settings
from p5r_assistant.guide.importer import import_guide_directory
from p5r_assistant.guide.repository import load_guide, save_guide
from p5r_assistant.guide.schema import Guide
from p5r_assistant.match.aliases import AliasStore
from p5r_assistant.ocr.rapidocr_engine import RapidOcrEngine
from p5r_assistant.recognition import RecognitionService
from p5r_assistant.ui.overlay import ConsoleOverlay


@dataclass(slots=True)
class RuntimePaths:
    data_dir: Path = Path("data")
    htmls_dir: Path = Path("htmls")
    debug_capture_dir: Path | None = None

    @property
    def guide_path(self) -> Path:
        return self.data_dir / "guide.json"

    @property
    def aliases_path(self) -> Path:
        return self.data_dir / "aliases.json"

    @property
    def settings_path(self) -> Path:
        return self.data_dir / "settings.json"


def ensure_guide(paths: RuntimePaths) -> Guide:
    if paths.guide_path.exists():
        return load_guide(paths.guide_path)
    guide, _report = import_guide_directory(paths.htmls_dir)
    save_guide(guide, paths.guide_path)
    return guide


def ensure_runtime_files(paths: RuntimePaths) -> None:
    load_settings(paths.settings_path)
    AliasStore.load(paths.aliases_path)
    ensure_guide(paths)


def build_recognition_service(paths: RuntimePaths, capture=None, ocr=None, overlay=None) -> RecognitionService:
    settings = load_settings(paths.settings_path)
    guide = ensure_guide(paths)
    aliases = AliasStore.load(paths.aliases_path)
    capture = capture or P5RChoiceRegionCapture(settings.crop_region, debug_capture_dir=paths.debug_capture_dir)
    ocr = ocr or RapidOcrEngine()
    overlay = overlay or ConsoleOverlay()
    return RecognitionService(capture, ocr, guide, aliases, overlay)


class LazyRecognitionService:
    def __init__(self, paths: RuntimePaths, overlay=None) -> None:
        self.paths = paths
        self.overlay = overlay or ConsoleOverlay()
        self._service: RecognitionService | None = None

    def recognize_once(self):
        if self._service is None:
            self._service = build_recognition_service(self.paths, overlay=self.overlay)
        return self._service.recognize_once()
