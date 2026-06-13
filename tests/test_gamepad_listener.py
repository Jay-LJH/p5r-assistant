from p5r_assistant.input.gamepad import GamepadComboListener


def test_gamepad_listener_triggers_when_combo_is_pressed_once():
    calls = []
    listener = GamepadComboListener(["LB", "RB", "Y"], lambda: calls.append("hit"))

    listener.handle_buttons({"LB", "RB", "Y"})
    listener.handle_buttons({"LB", "RB", "Y"})
    listener.handle_buttons(set())
    listener.handle_buttons({"LB", "RB", "Y"})

    assert calls == ["hit", "hit"]


def test_gamepad_listener_does_not_trigger_partial_combo():
    calls = []
    listener = GamepadComboListener(["LB", "RB", "Y"], lambda: calls.append("hit"))

    listener.handle_buttons({"LB", "RB"})

    assert calls == []
