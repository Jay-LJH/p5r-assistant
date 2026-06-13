from p5r_assistant.guide.schema import Choice, Confidant, Event, Guide, Question
from p5r_assistant.match.aliases import AliasStore
from p5r_assistant.match.matcher import Matcher
from p5r_assistant.match.normalize import normalize_text
from p5r_assistant.ui.overlay import format_candidates, format_recommendation


def _result():
    choices = [
        Choice("c1", 1, "什么意思？", normalize_text("什么意思？"), 0),
        Choice("c2", 2, "随便他们怎么说吧", normalize_text("随便他们怎么说吧"), 3),
    ]
    guide = Guide(1, "now", "tests", [Confidant("ann", "高卷杏", [Event("e1", "rank_up", [Question("q1", choices)], 1, 2)])])
    return Matcher(guide, AliasStore.empty()).match(["什么意思？", "随便他们怎么说吧"])


def test_format_recommendation_contains_overlay_fields():
    text = format_recommendation(_result())

    assert "P5R Assistant" in text
    assert "推荐：第 2 项 随便他们怎么说吧" in text
    assert "好感：3" in text
    assert "高卷杏 / Rank 2" in text


def test_format_candidates_contains_candidate_lines():
    text = format_candidates(_result())

    assert "匹配不确定" in text
    assert "高卷杏 Rank 2 第 2 项" in text
