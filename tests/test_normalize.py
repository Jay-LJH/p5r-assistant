from p5r_assistant.match.normalize import normalize_text


def test_normalizes_spacing_width_and_punctuation():
    assert normalize_text(" 你　说 什么？！ ") == "你说什么?!"


def test_normalizes_ellipsis_and_quotes():
    assert normalize_text("“这样啊……”") == '"这样啊..."'


def test_removes_common_ocr_noise():
    assert normalize_text("随便|他们怎么 说吧") == "随便他们怎么说吧"
