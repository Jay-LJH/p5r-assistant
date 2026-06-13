from p5r_assistant.capture.choice_region import P5RChoiceRegionCapture
from p5r_assistant.capture.window_finder import WindowInfo
from p5r_assistant.config.settings import CropRegion


class FakeImage:
    size = (100, 100)

    def crop(self, box):
        left, top, right, bottom = box
        cropped = FakeImage()
        cropped.size = (right - left, bottom - top)
        return cropped


def test_choice_region_capture_finds_window_screenshots_and_crops():
    image = FakeImage()
    capture = P5RChoiceRegionCapture(
        crop_region=CropRegion(left=0.1, top=0.2, width=0.3, height=0.4),
        window_finder=lambda: WindowInfo(1, "P5R", 10, 20, 100, 100),
        screenshotter=lambda window: image,
        preprocessor=lambda crop: crop,
    )

    crop = capture.capture_choice_region()

    assert crop.size == (30, 40)
