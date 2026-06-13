from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from tempfile import NamedTemporaryFile


@dataclass(slots=True)
class CropRegion:
    left: float = 0.08
    top: float = 0.58
    width: float = 0.84
    height: float = 0.32


@dataclass(slots=True)
class AppSettings:
    keyboard_hotkey: str = "ctrl+alt+p"
    controller_combo: list[str] = field(default_factory=lambda: ["LB", "RB", "Y"])
    ocr_engine: str = "rapidocr"
    confidence_direct: float = 0.85
    confidence_uncertain: float = 0.65
    overlay_position: str = "top-right"
    overlay_timeout_seconds: int = 5
    crop_region: CropRegion = field(default_factory=CropRegion)

    @classmethod
    def from_dict(cls, data: dict) -> "AppSettings":
        crop = data.get("crop_region", {})
        return cls(
            keyboard_hotkey=data.get("keyboard_hotkey", "ctrl+alt+p"),
            controller_combo=list(data.get("controller_combo", ["LB", "RB", "Y"])),
            ocr_engine=data.get("ocr_engine", "rapidocr"),
            confidence_direct=float(data.get("confidence_direct", 0.85)),
            confidence_uncertain=float(data.get("confidence_uncertain", 0.65)),
            overlay_position=data.get("overlay_position", "top-right"),
            overlay_timeout_seconds=int(data.get("overlay_timeout_seconds", 5)),
            crop_region=CropRegion(**crop) if isinstance(crop, dict) else CropRegion(),
        )


def _atomic_write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as tmp:
        json.dump(payload, tmp, ensure_ascii=False, indent=2)
        tmp.write("\n")
        temp_path = Path(tmp.name)
    temp_path.replace(path)


def save_settings(settings: AppSettings, path: Path) -> None:
    _atomic_write_json(path, asdict(settings))


def load_settings(path: Path) -> AppSettings:
    if not path.exists():
        settings = AppSettings()
        save_settings(settings, path)
        return settings
    return AppSettings.from_dict(json.loads(path.read_text(encoding="utf-8")))
