from p5r_assistant.guide.schema import Choice, Confidant, Event, Guide, Question
from p5r_assistant.match.aliases import AliasStore
from p5r_assistant.match.matcher import Matcher
from p5r_assistant.match.normalize import normalize_text
from p5r_assistant.ui.overlay import format_recommendation_rich_text


def test_format_recommendation_rich_text_emphasizes_romance_condition():
    romance_text = "\u8fd9\u662f\u5927\u5b85\u7684\u9b45\u529b\uff08\u604b\u4eba\u6761\u4ef61\uff09"
    choices = [
        Choice("c1", 1, "\u666e\u901a\u9009\u9879", normalize_text("\u666e\u901a\u9009\u9879"), 0),
        Choice("c2", 2, romance_text, normalize_text(romance_text), 3),
    ]
    guide = Guide(
        1,
        "now",
        "tests",
        [Confidant("ann", "\u9ad8\u5377\u674f", [Event("e1", "rank_up", [Question("q1", choices)], 1, 2)])],
    )
    result = Matcher(guide, AliasStore.empty()).match(["\u666e\u901a\u9009\u9879", romance_text])

    text = format_recommendation_rich_text(result)

    assert "<html>" in text
    assert "\u8fd9\u662f\u5927\u5b85\u7684\u9b45\u529b" in text
    assert '<span class="romance-condition">\uff08\u604b\u4eba\u6761\u4ef61\uff09</span>' in text
