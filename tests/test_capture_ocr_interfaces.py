from p5r_assistant.capture.crop import RelativeCrop, crop_box
from p5r_assistant.ocr.engine import OcrLine, group_option_lines


def test_relative_crop_box_uses_window_dimensions():
    region = RelativeCrop(left=0.1, top=0.5, width=0.8, height=0.25)

    assert crop_box(1920, 1080, region) == (192, 540, 1728, 810)


def test_crop_box_clamps_to_window_bounds():
    region = RelativeCrop(left=-0.1, top=0.9, width=1.5, height=0.4)

    assert crop_box(100, 100, region) == (0, 90, 100, 100)


def test_group_option_lines_filters_low_confidence_and_sorts():
    lines = [
        OcrLine(text="第二项", confidence=0.9, box=(0, 30, 50, 40)),
        OcrLine(text="噪声", confidence=0.1, box=(0, 15, 50, 20)),
        OcrLine(text="第一项", confidence=0.8, box=(0, 0, 50, 10)),
    ]

    assert group_option_lines(lines, min_confidence=0.5) == ["第一项", "第二项"]
