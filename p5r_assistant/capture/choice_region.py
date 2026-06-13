from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from p5r_assistant.capture.crop import RelativeCrop, crop_image
from p5r_assistant.capture.screenshot import screenshot_window
from p5r_assistant.capture.window_finder import WindowInfo, find_p5r_window
from p5r_assistant.config.settings import CropRegion
from p5r_assistant.ocr.preprocess import preprocess_for_ocr


class P5RChoiceRegionCapture:
    def __init__(
        self,
        crop_region: CropRegion,
        window_finder: Callable[[], WindowInfo] = find_p5r_window,
        screenshotter: Callable[[WindowInfo], object] = screenshot_window,
        preprocessor: Callable[[object], object] = preprocess_for_ocr,
        debug_capture_dir: Path | None = None,
    ) -> None:
        self.crop_region = crop_region
        self.window_finder = window_finder
        self.screenshotter = screenshotter
        self.preprocessor = preprocessor
        self.debug_capture_dir = debug_capture_dir

    def capture_choice_region(self):
        window = self.window_finder()
        screenshot = self.screenshotter(window)
        self._save_debug_image(screenshot, "debug-full-window.png")
        region = RelativeCrop(
            left=self.crop_region.left,
            top=self.crop_region.top,
            width=self.crop_region.width,
            height=self.crop_region.height,
        )
        cropped = crop_image(screenshot, region)
        self._save_debug_image(cropped, "debug-choice-region.png")
        return self.preprocessor(cropped)

    def _save_debug_image(self, image, filename: str) -> None:
        if self.debug_capture_dir is None or not hasattr(image, "save"):
            return
        self.debug_capture_dir.mkdir(parents=True, exist_ok=True)
        image.save(self.debug_capture_dir / filename)
