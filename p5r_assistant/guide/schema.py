from __future__ import annotations

from dataclasses import asdict, dataclass, field


@dataclass(slots=True)
class Choice:
    id: str
    index: int
    text: str
    normalized: str
    points: int = 0

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass(slots=True)
class Question:
    id: str
    choices: list[Choice]

    def to_dict(self) -> dict:
        return {"id": self.id, "choices": [choice.to_dict() for choice in self.choices]}


@dataclass(slots=True)
class Event:
    id: str
    type: str
    questions: list[Question]
    rank_from: int | None = None
    rank_to: int | None = None
    title: str = ""

    def to_dict(self) -> dict:
        data = asdict(self)
        data["questions"] = [question.to_dict() for question in self.questions]
        return data


@dataclass(slots=True)
class Confidant:
    id: str
    name: str
    events: list[Event] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {"id": self.id, "name": self.name, "events": [event.to_dict() for event in self.events]}


@dataclass(slots=True)
class Guide:
    version: int
    generated_at: str
    source_dir: str
    confidants: list[Confidant]

    def to_dict(self) -> dict:
        return {
            "version": self.version,
            "generated_at": self.generated_at,
            "source_dir": self.source_dir,
            "confidants": [confidant.to_dict() for confidant in self.confidants],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Guide":
        confidants = []
        for confidant_data in data.get("confidants", []):
            events = []
            for event_data in confidant_data.get("events", []):
                questions = []
                for question_data in event_data.get("questions", []):
                    choices = [Choice(**choice_data) for choice_data in question_data.get("choices", [])]
                    questions.append(Question(id=question_data["id"], choices=choices))
                events.append(
                    Event(
                        id=event_data["id"],
                        type=event_data.get("type", "unknown"),
                        rank_from=event_data.get("rank_from"),
                        rank_to=event_data.get("rank_to"),
                        title=event_data.get("title", ""),
                        questions=questions,
                    )
                )
            confidants.append(Confidant(id=confidant_data["id"], name=confidant_data["name"], events=events))
        return cls(
            version=int(data.get("version", 1)),
            generated_at=data.get("generated_at", ""),
            source_dir=data.get("source_dir", ""),
            confidants=confidants,
        )
