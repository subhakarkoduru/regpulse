"""Fetch bulletins and guide snapshots from public regulatory sources.

Week 1: exactly ONE source. Get it working end to end before adding more.

Two separate jobs:
  * fetch_latest_bulletins  — the *trigger*: what was announced, and when.
  * fetch_guide_snapshot    — the *diff input*: the guide sections as of a date.
Bulletins mostly summarize changes; the section-level diff needs the guide.
"""

from __future__ import annotations

from datetime import date

from .models import Bulletin, GuideSnapshot


def fetch_latest_bulletins(source: str, since: date | None = None) -> list[Bulletin]:
    """Fetch bulletins from `source` published after `since`.

    Raises on fetch/parse failure — the caller decides retry policy.
    """
    raise NotImplementedError("Week 1, step 2: implement for one source first")


def fetch_guide_snapshot(source: str, section_ids: list[str] | None = None) -> GuideSnapshot:
    """Fetch the current guide text for `source` (optionally only `section_ids`).

    Persist each snapshot so the next run can diff against it.
    """
    raise NotImplementedError("Week 1, step 2: implement alongside the bulletin fetcher")
