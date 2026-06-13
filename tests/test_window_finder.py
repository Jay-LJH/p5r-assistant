import sys
from types import SimpleNamespace

from p5r_assistant.capture import window_finder
from p5r_assistant.capture.window_finder import is_p5r_window_title


def test_p5r_window_title_accepts_chinese_release_title():
    assert is_p5r_window_title("濂崇寮傞椈褰?鐨囧鐗?")


def test_p5r_window_title_accepts_english_release_title():
    assert is_p5r_window_title("Persona 5 Royal")


def test_p5r_window_title_rejects_project_editor_title():
    assert not is_p5r_window_title("P5R Assistant - Visual Studio Code")


def test_find_p5r_window_sets_dpi_awareness_before_reading_rect(monkeypatch):
    calls = []

    def fake_ensure_process_dpi_aware():
        calls.append("dpi")

    def fake_enum_windows(callback, arg):
        calls.append("enum")
        callback(123, arg)

    def fake_get_window_rect(hwnd):
        calls.append("rect")
        return (10, 20, 210, 120)

    fake_win32gui = SimpleNamespace(
        EnumWindows=fake_enum_windows,
        GetWindowText=lambda hwnd: "Persona 5 Royal",
        GetWindowRect=fake_get_window_rect,
    )
    monkeypatch.setitem(sys.modules, "win32gui", fake_win32gui)
    monkeypatch.setattr(window_finder, "ensure_process_dpi_aware", fake_ensure_process_dpi_aware)

    found = window_finder.find_p5r_window()

    assert found.left == 10
    assert calls == ["dpi", "enum", "rect"]
