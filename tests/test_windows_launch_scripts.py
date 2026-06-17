from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_powershell_launch_script_sets_utf8_and_runs_persistent_tray_mode():
    path = ROOT / "run.ps1"

    assert path.exists()

    script = path.read_text(encoding="utf-8")
    assert "[Console]::OutputEncoding" in script
    assert "[Console]::InputEncoding" in script
    assert "$OutputEncoding" in script
    assert "PYTHONUTF8" in script
    assert "PYTHONIOENCODING" in script
    assert "python -m p5r_assistant.app run" in script


def test_cmd_launch_script_sets_utf8_and_runs_persistent_tray_mode():
    path = ROOT / "run.cmd"

    assert path.exists()

    script = path.read_text(encoding="utf-8")
    assert "chcp 65001" in script
    assert "PYTHONUTF8" in script
    assert "PYTHONIOENCODING" in script
    assert "python -m p5r_assistant.app run" in script
