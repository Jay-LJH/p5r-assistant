from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class RelativeCrop:
    left: float
    top: float
    width: float
    height: float


def crop_box(window_width: int, window_height: int, region: RelativeCrop) -> tuple[int, int, int, int]:
    left = int(window_width * region.left)
    top = int(window_height * region.top)
    right = int(window_width * (region.left + region.width))
    bottom = int(window_height * (region.top + region.height))
    return (
        max(0, min(window_width, left)),
        max(0, min(window_height, top)),
        max(0, min(window_width, right)),
        max(0, min(window_height, bottom)),
    )


def crop_image(image, region: RelativeCrop):
    width, height = image.size
    return image.crop(crop_box(width, height, region))
