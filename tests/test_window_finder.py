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


def test_find_p5r_window_uses_extended_frame_bounds_for_borderless(monkeypatch):
    fake_win32gui = SimpleNamespace(
        EnumWindows=lambda callback, arg: callback(123, arg),
        GetWindowText=lambda hwnd: "Persona 5 Royal",
        GetWindowRect=lambda hwnd: (8, 9, 1930, 1089),
        IsWindowVisible=lambda hwnd: True,
        IsIconic=lambda hwnd: False,
        GetForegroundWindow=lambda: 0,
    )
    monkeypatch.setitem(sys.modules, "win32gui", fake_win32gui)
    monkeypatch.setattr(window_finder, "ensure_process_dpi_aware", lambda: None)
    monkeypatch.setattr(
        window_finder,
        "_get_extended_frame_bounds",
        lambda hwnd: (0, 0, 1920, 1080),
    )

    found = window_finder.find_p5r_window()

    assert found.left == 0
    assert found.top == 0
    assert found.width == 1920
    assert found.height == 1080


def test_find_p5r_window_skips_invisible_and_minimized_windows(monkeypatch):
    def fake_enum_windows(callback, arg):
        callback(1, arg)
        callback(2, arg)
        callback(3, arg)

    fake_win32gui = SimpleNamespace(
        EnumWindows=fake_enum_windows,
        GetWindowText=lambda hwnd: "Persona 5 Royal",
        GetWindowRect=lambda hwnd: (10 * hwnd, 0, 10 * hwnd + 100, 100),
        IsWindowVisible=lambda hwnd: hwnd != 1,
        IsIconic=lambda hwnd: hwnd == 2,
        GetForegroundWindow=lambda: 0,
    )
    monkeypatch.setitem(sys.modules, "win32gui", fake_win32gui)
    monkeypatch.setattr(window_finder, "ensure_process_dpi_aware", lambda: None)
    monkeypatch.setattr(window_finder, "_get_extended_frame_bounds", lambda hwnd: None)

    found = window_finder.find_p5r_window()

    assert found.handle == 3
    assert found.left == 30


def test_find_p5r_window_prefers_foreground_game_window(monkeypatch):
    def fake_enum_windows(callback, arg):
        callback(1, arg)
        callback(2, arg)

    fake_win32gui = SimpleNamespace(
        EnumWindows=fake_enum_windows,
        GetWindowText=lambda hwnd: "Persona 5 Royal",
        GetWindowRect=lambda hwnd: (10 * hwnd, 0, 10 * hwnd + 100, 100),
        IsWindowVisible=lambda hwnd: True,
        IsIconic=lambda hwnd: False,
        GetForegroundWindow=lambda: 2,
    )
    monkeypatch.setitem(sys.modules, "win32gui", fake_win32gui)
    monkeypatch.setattr(window_finder, "ensure_process_dpi_aware", lambda: None)
    monkeypatch.setattr(window_finder, "_get_extended_frame_bounds", lambda hwnd: None)

    found = window_finder.find_p5r_window()

    assert found.handle == 2
    assert found.left == 20


def test_find_p5r_window_falls_back_to_screen_bounds_for_foreground_fullscreen(monkeypatch):
    fake_win32gui = SimpleNamespace(
        EnumWindows=lambda callback, arg: None,
        GetWindowText=lambda hwnd: "Persona 5 Royal",
        GetWindowRect=lambda hwnd: (0, 0, 0, 0),
        IsWindowVisible=lambda hwnd: True,
        IsIconic=lambda hwnd: False,
        GetForegroundWindow=lambda: 99,
    )
    monkeypatch.setitem(sys.modules, "win32gui", fake_win32gui)
    monkeypatch.setattr(window_finder, "ensure_process_dpi_aware", lambda: None)
    monkeypatch.setattr(window_finder, "_get_extended_frame_bounds", lambda hwnd: None)
    monkeypatch.setattr(window_finder, "_get_virtual_screen_bounds", lambda: (0, 0, 2560, 1440))

    found = window_finder.find_p5r_window()

    assert found == window_finder.WindowInfo(99, "Persona 5 Royal", 0, 0, 2560, 1440)
