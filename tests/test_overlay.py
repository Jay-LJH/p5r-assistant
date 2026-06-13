from p5r_assistant.guide.schema import Choice, Confidant, Event, Guide, Question
from p5r_assistant.match.matcher import Matcher
from p5r_assistant.match.aliases import AliasStore
from p5r_assistant.match.normalize import normalize_text
from p5r_assistant.ui.overlay import ConsoleOverlay


def test_console_overlay_imports_and_prints_recommendation(capsys):
    choices = [
        Choice("c1", 1, "什么意思？", normalize_text("什么意思？"), 0),
        Choice("c2", 2, "随便他们怎么说吧", normalize_text("随便他们怎么说吧"), 3),
    ]
    guide = Guide(1, "now", "tests", [Confidant("ann", "高卷杏", [Event("e1", "rank_up", [Question("q1", choices)], 1, 2)])])
    result = Matcher(guide, AliasStore.empty()).match(["什么意思？", "随便他们怎么说吧"])

    ConsoleOverlay().show_recommendation(result)

    output = capsys.readouterr().out
    assert "推荐：第 2 项" in output
    assert "随便他们怎么说吧" in output
