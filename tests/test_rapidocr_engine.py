import numpy as np
from PIL import Image

from p5r_assistant.ocr.rapidocr_engine import RapidOcrEngine


class FakeRapidOCR:
    def __init__(self):
        self.seen = None

    def __call__(self, image):
        self.seen = image
        return [], None


def test_rapidocr_engine_converts_pil_image_to_numpy_array():
    fake = FakeRapidOCR()
    engine = RapidOcrEngine.__new__(RapidOcrEngine)
    engine._engine = fake

    image = Image.new("RGB", (8, 6), "white")
    lines = engine.recognize(image)

    assert lines == []
    assert isinstance(fake.seen, np.ndarray)
    assert fake.seen.shape == (6, 8, 3)
