from __future__ import annotations


def preprocess_for_ocr(image, scale: int = 2):
    try:
        from PIL import ImageEnhance
    except ImportError:  # pragma: no cover
        return image

    width, height = image.size
    image = image.resize((width * scale, height * scale))
    image = image.convert("L")
    return ImageEnhance.Contrast(image).enhance(1.8)
