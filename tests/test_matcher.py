from p5r_assistant.guide.schema import Choice, Confidant, Event, Guide, Question
from p5r_assistant.match.aliases import AliasEntry, AliasStore
from p5r_assistant.match.matcher import Matcher
from p5r_assistant.match.normalize import normalize_text


def _guide() -> Guide:
    choices = [
        Choice("ann_rank_2_q1_c1", 1, "什么意思？", normalize_text("什么意思？"), 0),
        Choice("ann_rank_2_q1_c2", 2, "随便他们怎么说吧", normalize_text("随便他们怎么说吧"), 3),
    ]
    question = Question("ann_rank_2_q1", choices)
    event = Event("ann_rank_2", "rank_up", [question], rank_from=1, rank_to=2, title="Rank 2")
    return Guide("1", "now", "tests", [Confidant("ann", "高卷杏", [event])])


def test_exact_option_group_recommends_highest_points():
    result = Matcher(_guide(), AliasStore.empty()).match(["什么意思？", "随便他们怎么说吧"])

    assert result.confident is True
    assert result.recommendation.choice.index == 2
    assert result.recommendation.choice.points == 3


def test_fuzzy_ocr_typo_still_matches():
    result = Matcher(_guide(), AliasStore.empty()).match(["什么思？", "随便他们怎幺说吧"])

    assert result.score >= 0.65
    assert result.recommendation.choice.id == "ann_rank_2_q1_c2"


def test_alias_improves_match_score():
    alias_store = AliasStore(
        [
            AliasEntry(
                ocr_text="隨便他們怎麼説吧",
                canonical_text="随便他们怎么说吧",
                choice_id="ann_rank_2_q1_c2",
                created_at="2026-06-14T00:00:00+08:00",
            )
        ]
    )

    result = Matcher(_guide(), alias_store).match(["什么意思？", "隨便他們怎麼説吧"])

    assert result.score >= 0.85
    assert result.alias_hits == 1


def test_low_confidence_returns_candidates_without_hard_recommendation():
    result = Matcher(_guide(), AliasStore.empty()).match(["完全不同", "看不清"])

    assert result.confident is False
    assert result.recommendation is None
    assert result.candidates
