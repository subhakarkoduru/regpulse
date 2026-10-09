"""Regulatory-specific data models for RegPulse.

Domain-neutral types (ChangeEvent, Citation, ImpactBrief) live in
regpulse.core so HazardLens can share them.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from .core.events import ChangeEvent

ChangeType = Literal["added", "removed", "modified"]


@dataclass
class GuideSection:
    """One section of a selling guide / rule document."""

    section_id: str  # stable identifier, e.g. "B3-3.1-09"
    heading: str
    body: str


@dataclass
class GuideSnapshot:
    """The full guide (or the slice we track) as of one date.

    Bulletins mostly *summarize* changes; the section-by-section diff runs
    between two snapshots of the guide itself, with the bulletin as trigger.
    """

    source: str
    as_of: str  # ISO date or guide edition label
    sections: list[GuideSection] = field(default_factory=list)


@dataclass(kw_only=True)
class Bulletin(ChangeEvent):
    """A regulatory bulletin / announcement / notice."""

    kind: str = "regulatory"
    affected_section_ids: list[str] = field(default_factory=list)


@dataclass
class SectionDiff:
    """The diff of one section between two guide versions."""

    section_id: str
    change_type: ChangeType
    old_heading: str = ""
    new_heading: str = ""
    old_text: str = ""
    new_text: str = ""
