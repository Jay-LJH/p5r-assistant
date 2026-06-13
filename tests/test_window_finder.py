from p5r_assistant.capture.window_finder import is_p5r_window_title


def test_p5r_window_title_accepts_chinese_release_title():
    assert is_p5r_window_title("濂崇寮傞椈褰?鐨囧鐗?")


def test_p5r_window_title_accepts_english_release_title():
    assert is_p5r_window_title("Persona 5 Royal")


def test_p5r_window_title_rejects_project_editor_title():
    assert not is_p5r_window_title("P5R Assistant - Visual Studio Code")
