from pathlib import Path

from p5r_assistant.config.settings import AppSettings, load_settings, save_settings
from p5r_assistant.match.aliases import AliasEntry, AliasStore


def test_settings_defaults_are_created(tmp_path: Path):
    path = tmp_path / "settings.json"

    settings = load_settings(path)

    assert settings.keyboard_hotkey == "ctrl+alt+p"
    assert settings.controller_combo == ["LB", "RB", "Y"]
    assert settings.crop_region.left == 0.46
    assert settings.crop_region.top == 0.48
    assert settings.crop_region.width == 0.38
    assert settings.crop_region.height == 0.35
    assert path.exists()


def test_settings_round_trip(tmp_path: Path):
    path = tmp_path / "settings.json"
    settings = AppSettings(confidence_direct=0.9, overlay_timeout_seconds=4)

    save_settings(settings, path)
    loaded = load_settings(path)

    assert loaded.confidence_direct == 0.9
    assert loaded.overlay_timeout_seconds == 4


def test_alias_store_round_trip(tmp_path: Path):
    path = tmp_path / "aliases.json"
    store = AliasStore(
        [
            AliasEntry(
                ocr_text="隨他們怎麼說吧",
                canonical_text="随便他们怎么说吧",
                choice_id="ann_rank_2_q1_c2",
                created_at="2026-06-14T00:00:00+08:00",
            )
        ]
    )

    store.save(path)
    loaded = AliasStore.load(path)

    assert loaded.resolve("隨他們怎麼說吧") == "随便他们怎么说吧"
    assert loaded.entries[0].choice_id == "ann_rank_2_q1_c2"
