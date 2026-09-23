"""Fetch bulletins from public regulatory sources.

Week 1: exactly ONE source. Get it working end to end before adding more.
"""

from __future__ import annotations

from datetime import date

from .models import Bulletin


def fetch_latest_bulletins(source: str, since: date | None = None) -> list[Bulletin]:
    """Fetch bulletins from `source` published after `since`.

    Returns Bulletin objects with sections populated. Raises on fetch/parse
    failure — the caller decides retry policy.
    """
    raise NotImplementedError("Week 1, step 2: implement for one source first")
