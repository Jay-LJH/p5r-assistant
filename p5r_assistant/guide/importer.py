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


def _parse_points(text: str) -> int:
    match = re.search(r"[-+]?\d+", text)
    return int(match.group(0)) if match else 0


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


def import_guide_file(path: Path) -> tuple[Confidant, ImportReport]:
    soup = BeautifulSoup(path.read_text(encoding="utf-8", errors="ignore"), "lxml")
    report = ImportReport(files_parsed=1)
    name = _extract_name(soup, path)
    confidant_id = _slug(name)
    events: list[Event] = []

    current_rank: int | None = None
    current_title = ""
    for element in soup.find_all(["h1", "h2", "h3", "h4", "table"]):
        if element.name != "table":
            heading = element.get_text(" ", strip=True)
            rank = _rank_from_heading(heading)
            if rank is not None:
                current_rank = rank
                current_title = heading
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
    return guide, report
