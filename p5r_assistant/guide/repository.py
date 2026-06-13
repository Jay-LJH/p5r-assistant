from __future__ import annotations

import json
from pathlib import Path

from p5r_assistant.config.settings import _atomic_write_json
from p5r_assistant.guide.schema import Guide


def save_guide(guide: Guide, path: Path) -> None:
    _atomic_write_json(path, guide.to_dict())


def load_guide(path: Path) -> Guide:
    return Guide.from_dict(json.loads(path.read_text(encoding="utf-8")))
