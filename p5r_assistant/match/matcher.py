from __future__ import annotations

from dataclasses import dataclass
from difflib import SequenceMatcher

from p5r_assistant.guide.schema import Choice, Confidant, Event, Guide, Question
from p5r_assistant.match.aliases import AliasStore
from p5r_assistant.match.normalize import normalize_text

try:
    from rapidfuzz import fuzz
except ImportError:  # pragma: no cover
    fuzz = None

ROMANCE_CONDITION_MARKERS = ("恋人条件", "戀人條件")


@dataclass(slots=True)
class Recommendation:
    confidant: Confidant
    event: Event
    question: Question
    choice: Choice
    score: float

    def to_dict(self) -> dict:
        return {
            "confidant": self.confidant.name,
            "event_id": self.event.id,
            "rank_to": self.event.rank_to,
            "question_id": self.question.id,
            "choice": self.choice.to_dict(),
            "score": round(self.score, 4),
        }


@dataclass(slots=True)
class MatchResult:
    score: float
    confident: bool
    uncertain: bool
    recommendation: Recommendation | None
    candidates: list[Recommendation]
    alias_hits: int = 0

    def to_dict(self) -> dict:
        return {
            "score": round(self.score, 4),
            "confident": self.confident,
            "uncertain": self.uncertain,
            "alias_hits": self.alias_hits,
            "recommendation": self.recommendation.to_dict() if self.recommendation else None,
            "candidates": [candidate.to_dict() for candidate in self.candidates],
        }


class Matcher:
    def __init__(
        self,
        guide: Guide,
        aliases: AliasStore,
        direct_threshold: float = 0.85,
        uncertain_threshold: float = 0.65,
    ) -> None:
        self.guide = guide
        self.aliases = aliases
        self.direct_threshold = direct_threshold
        self.uncertain_threshold = uncertain_threshold

    def match(self, visible_choices: list[str]) -> MatchResult:
        normalized_visible, alias_hits = self._normalize_visible(visible_choices)
        candidates: list[Recommendation] = []
        for confidant in self.guide.confidants:
            for event in confidant.events:
                for question in event.questions:
                    score = self._score_question(normalized_visible, question)
                    best_choice = max(question.choices, key=_choice_priority)
                    candidates.append(Recommendation(confidant, event, question, best_choice, score))

        candidates.sort(key=lambda candidate: candidate.score, reverse=True)
        best = candidates[0] if candidates else None
        if best is None:
            return MatchResult(0.0, False, False, None, [], alias_hits)

        confident = best.score >= self.direct_threshold
        uncertain = self.uncertain_threshold <= best.score < self.direct_threshold
        recommendation = best if confident or uncertain else None
        if not confident and not uncertain:
            recommendation = None
        return MatchResult(
            score=best.score,
            confident=confident,
            uncertain=uncertain,
            recommendation=recommendation,
            candidates=candidates[:5],
            alias_hits=alias_hits,
        )

    def _normalize_visible(self, visible_choices: list[str]) -> tuple[list[str], int]:
        normalized: list[str] = []
        alias_hits = 0
        for text in visible_choices:
            alias = self.aliases.resolve(text)
            if alias is not None:
                alias_hits += 1
                text = alias
            normalized.append(normalize_text(text))
        return normalized, alias_hits

    def _score_question(self, visible_choices: list[str], question: Question) -> float:
        guide_choices = [choice.normalized or normalize_text(choice.text) for choice in question.choices]
        if not visible_choices or not guide_choices:
            return 0.0

        count_score = 1.0 - min(abs(len(visible_choices) - len(guide_choices)), 3) * 0.2
        pair_scores = []
        for index, visible in enumerate(visible_choices):
            if index < len(guide_choices):
                pair_scores.append(_similarity(visible, guide_choices[index]))
            else:
                pair_scores.append(max(_similarity(visible, guide) for guide in guide_choices))
        text_score = sum(pair_scores) / len(pair_scores)
        group_score = _similarity("".join(visible_choices), "".join(guide_choices))
        return max(0.0, min(1.0, text_score * 0.65 + group_score * 0.25 + count_score * 0.10))


def _similarity(left: str, right: str) -> float:
    if left == right:
        return 1.0
    if fuzz is not None:
        return fuzz.ratio(left, right) / 100
    return SequenceMatcher(None, left, right).ratio()


def _choice_priority(choice: Choice) -> tuple[bool, int]:
    return (any(marker in choice.text for marker in ROMANCE_CONDITION_MARKERS), choice.points)
