"""Core data models for RegPulse."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date


@dataclass
class GuideSection:
    """One section of a selling guide / rule document."""

    section_id: str  # stable identifier, e.g. "B3-3.1-09"
    heading: str
    body: str


@dataclass
class Bulletin:
    """A single regulatory bulletin / notice."""

    bulletin_id: str
    source: str  # e.g. "fannie Mae selling guide", "CFPB", "FHFA"
    title: str
    published: date | None
    url: str
    sections: list[GuideSection] = field(default_factory=list)


@dataclass
class SectionDiff:
    """The diff of one section between two guide versions."""

    section_id: str
    change_type: str  # "added" | "removed" | "modified"
    old_text: str = ""
    new_text: str = ""
