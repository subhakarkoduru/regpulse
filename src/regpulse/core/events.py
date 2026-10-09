"""The generic 'something changed in the outside world' event."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(kw_only=True)
class ChangeEvent:
    """An external change that may affect a lender's rules or portfolio.

    RegPulse: a GSE bulletin, CFPB rule, or FHFA notice (kind="regulatory").
    HazardLens: a seasonal climate outlook or hazard update (kind="climate").
    """

    event_id: str
    source: str  # e.g. "Fannie Mae Selling Guide", "CFPB", "NOAA CPC"
    kind: str  # "regulatory" | "climate" | ...
    title: str
    published: date | None
    url: str
