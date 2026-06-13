from __future__ import annotations

import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from bs4 import BeautifulSoup

from p5r_assistant.guide.schema import Choice, Confidant, Event, Guide, Question
from p5r_assistant.match.normalize import normalize_text


@dataclass(slots=True)
class ImportReport:
    files_parsed: int = 0
    warnings: list[str] = field(default_factory=list)

    def extend(self, other: "ImportReport") -> None:
        self.files_parsed += other.files_parsed
        self.warnings.extend(other.warnings)


def _slug(text: str) -> str:
    slug = re.sub(r"\W+", "_", normalize_text(text).lower()).strip("_")
    return slug or "confidant"


def _extract_name(soup: BeautifulSoup, path: Path) -> str:
    title = soup.title.get_text(" ", strip=True) if soup.title else path.stem
    return re.split(r"\s*-\s*", title)[0].strip() or path.stem


def _rank_from_heading(text: str) -> int | None:
    match = re.search(r"(?:Rank|RANK|coop|COOP)?\s*(\d{1,2})", text)
    return int(match.group(1)) if match else None


def _is_rank_up_section(text: str) -> bool:
    normalized = normalize_text(text).lower()
    return "提升事件" in normalized or "coop对话攻略" in normalized


def _is_non_rank_up_section(text: str) -> bool:
    normalized = normalize_text(text).lower()
    markers = (
        "rank等级提升效果",
        "等级提升效果",
        "p5r导航",
        "导航",
        "景点事件",
        "日常事件",
        "事件一览",
        "基本信息",
        "个人资料",
    )
    return any(marker in normalized for marker in markers)


def _parse_points(text: str) -> int:
    match = re.search(r"[-+]?\d+", text)
    return int(match.group(0)) if match else 0


def _is_no_points(text: str) -> bool:
    return text.strip() in {"", "-", "—", "－", "无"}


def _parse_table_rows(table) -> list[Choice]:
    choices: list[Choice] = []
    for row in table.find_all("tr"):
        cells = [cell.get_text(" ", strip=True) for cell in row.find_all(["td", "th"])]
        if not cells or any("选项" in cell for cell in cells) and len(cells) <= 2 and not re.search(r"\d", " ".join(cells)):
            continue
        text = cells[0].strip()
        if not text or len(normalize_text(text)) < 2:
            continue
        points = _parse_points(" ".join(cells[1:])) if len(cells) > 1 else 0
        choices.append(
            Choice(
                id="",
                index=len(choices) + 1,
                text=text,
                normalized=normalize_text(text),
                points=points,
            )
        )
    return choices


def _parse_rank_transition(text: str) -> int | None:
    match = re.search(r"\d+\s*[→>\-]\s*(\d+)", text)
    return int(match.group(1)) if match else None


def _looks_like_rank_up_grid(table) -> bool:
    text = normalize_text(table.get_text(" ", strip=True))
    has_rank_column = "等级" in text or "rank" in text.lower()
    has_choice_column = "选择项" in text or "选项" in text
    return "提升事件" in text and has_rank_column and has_choice_column


def _parse_rank_up_grid_table(table, confidant_id: str) -> list[Event]:
    events: list[Event] = []
    event_questions: dict[int, list[Question]] = {}
    current_rank_to: int | None = None
    current_question_choices: list[Choice] | None = None
    question_count_by_rank: dict[int, int] = {}

    for row in table.find_all("tr"):
        cells = [cell.get_text(" ", strip=True) for cell in row.find_all(["td", "th"])]
        if not cells:
            continue
        row_text = " ".join(cells)
        rank_to = _parse_rank_transition(row_text)
        if rank_to is not None:
            current_rank_to = rank_to
            current_question_choices = None
            event_questions.setdefault(rank_to, [])
            continue
        if current_rank_to is None:
            continue
        if any(marker in row_text for marker in ("等级", "选择项", "好感度", "触发条件")):
            continue

        choice_text = ""
        points_text = ""
        if len(cells) >= 3 and (cells[0].isdigit() or cells[0] == "电话"):
            choice_text = cells[1]
            points_text = cells[2]
            current_question_choices = []
            question_count_by_rank[current_rank_to] = question_count_by_rank.get(current_rank_to, 0) + 1
            question_id = f"{confidant_id}_rank_{current_rank_to}_q{question_count_by_rank[current_rank_to]}"
            question = Question(id=question_id, choices=current_question_choices)
            event_questions[current_rank_to].append(question)
        elif len(cells) >= 2 and current_question_choices is not None:
            choice_text = cells[0]
            points_text = cells[1]

        if not choice_text or choice_text in {"无", "—", "-", "－"}:
            continue
        if current_question_choices is None:
            continue
        current_question_choices.append(
            Choice(
                id="",
                index=len(current_question_choices) + 1,
                text=choice_text,
                normalized=normalize_text(choice_text),
                points=0 if _is_no_points(points_text) else _parse_points(points_text),
            )
        )

    for rank_to, questions in event_questions.items():
        questions = [question for question in questions if question.choices]
        if not questions:
            continue
        event_id = f"{confidant_id}_rank_{rank_to}"
        for question in questions:
            question.id = question.id.replace(f"{confidant_id}_rank_{rank_to}", event_id)
            for choice in question.choices:
                choice.id = f"{question.id}_c{choice.index}"
        events.append(
            Event(
                id=event_id,
                type="rank_up",
                rank_from=rank_to - 1 if rank_to > 1 else None,
                rank_to=rank_to,
                title=f"Rank {rank_to}",
                questions=questions,
            )
        )
    return events


def import_guide_file(path: Path) -> tuple[Confidant, ImportReport]:
    soup = BeautifulSoup(path.read_text(encoding="utf-8", errors="ignore"), "lxml")
    report = ImportReport(files_parsed=1)
    name = _extract_name(soup, path)
    confidant_id = _slug(name)
    events: list[Event] = []

    current_rank: int | None = None
    current_title = ""
    inside_rank_up_section = False
    saw_explicit_section = False
    for element in soup.find_all(["h1", "h2", "h3", "h4", "table"]):
        if element.name != "table":
            heading = element.get_text(" ", strip=True)
            if element.name in {"h1", "h2", "h3"}:
                if _is_rank_up_section(heading):
                    inside_rank_up_section = True
                    saw_explicit_section = True
                    current_rank = None
                    current_title = heading
                    continue
                if _is_non_rank_up_section(heading):
                    inside_rank_up_section = False
                    saw_explicit_section = True
                    current_rank = None
                    current_title = heading
                    continue
            rank = _rank_from_heading(heading)
            if rank is not None:
                current_rank = rank
                current_title = heading
            continue

        if inside_rank_up_section and _looks_like_rank_up_grid(element):
            events.extend(_parse_rank_up_grid_table(element, confidant_id))
            continue

        if not current_rank or (saw_explicit_section and not inside_rank_up_section):
            continue

        choices = _parse_table_rows(element)
        if not choices:
            report.warnings.append(f"{path.name}: unsupported or empty table")
            continue

        event_number = len(events) + 1
        event_id = f"{confidant_id}_rank_{current_rank or event_number}"
        question_id = f"{event_id}_q1"
        for choice in choices:
            choice.id = f"{question_id}_c{choice.index}"
        events.append(
            Event(
                id=event_id,
                type="rank_up" if current_rank else "unknown",
                rank_from=(current_rank - 1) if current_rank and current_rank > 1 else None,
                rank_to=current_rank,
                title=current_title,
                questions=[Question(id=question_id, choices=choices)],
            )
        )

    if not events:
        report.warnings.append(f"{path.name}: no guide tables parsed")
    return Confidant(id=confidant_id, name=name, events=events), report


def clean_guide(guide: Guide) -> Guide:
    confidants: list[Confidant] = []
    for confidant in guide.confidants:
        events = [
            event
            for event in confidant.events
            if event.type == "rank_up" and event.rank_to is not None and event.questions
        ]
        if events:
            confidants.append(Confidant(id=confidant.id, name=confidant.name, events=events))
    return Guide(
        version=guide.version,
        generated_at=guide.generated_at,
        source_dir=guide.source_dir,
        confidants=confidants,
    )


def import_guide_directory(source_dir: Path) -> tuple[Guide, ImportReport]:
    report = ImportReport()
    confidants: list[Confidant] = []
    for path in sorted(source_dir.glob("*.htm*")):
        confidant, file_report = import_guide_file(path)
        report.extend(file_report)
        if confidant.events:
            confidants.append(confidant)
    guide = Guide(
        version=1,
        generated_at=datetime.now().astimezone().isoformat(timespec="seconds"),
        source_dir=str(source_dir),
        confidants=confidants,
    )
    return clean_guide(guide), report
