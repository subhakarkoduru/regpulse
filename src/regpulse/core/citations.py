"""One citation format for every claim either project makes."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Citation:
    """Points a claim at the exact source text that supports it.

    `locator` is source-specific: a guide section id ("B3-6-02"), a FEMA
    NRI county FIPS code, a NOAA outlook product id, etc.
    """

    source: str
    locator: str
    url: str
    excerpt: str = ""  # short supporting span, never the whole document

    def __post_init__(self) -> None:
        if not self.source or not self.locator:
            raise ValueError("Citation needs both source and locator")
