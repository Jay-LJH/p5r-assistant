from p5r_assistant.ui.tray import DesktopAppConfig


def test_desktop_app_config_defaults_enable_inputs():
    config = DesktopAppConfig()

    assert config.enable_keyboard is True
    assert config.enable_gamepad is True


def test_desktop_app_config_can_disable_inputs():
    config = DesktopAppConfig(enable_keyboard=False, enable_gamepad=False)

    assert config.enable_keyboard is False
    assert config.enable_gamepad is False
