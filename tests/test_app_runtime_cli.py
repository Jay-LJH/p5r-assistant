from pathlib import Path

from p5r_assistant.app import build_parser
from p5r_assistant.runtime import RuntimePaths


def test_run_command_accepts_runtime_paths():
    args = build_parser().parse_args(
        [
            "run",
            "--data-dir",
            "runtime-data",
            "--htmls",
            "runtime-htmls",
            "--no-keyboard",
            "--no-gamepad",
        ]
    )

    assert args.command == "run"
    assert args.data_dir == "runtime-data"
    assert args.htmls == "runtime-htmls"
    assert args.no_keyboard is True
    assert args.no_gamepad is True


def test_runtime_paths_resolve_expected_files():
    paths = RuntimePaths(data_dir=Path("runtime-data"), htmls_dir=Path("runtime-htmls"))

    assert paths.guide_path == Path("runtime-data") / "guide.json"
    assert paths.settings_path == Path("runtime-data") / "settings.json"
    assert paths.aliases_path == Path("runtime-data") / "aliases.json"
