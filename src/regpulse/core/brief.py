"""The shared output contract: an ImpactBrief."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from .citations import Citation
from .events import ChangeEvent

Confidence = Literal["high", "medium", "low"]

# Why a claim is believed. Keeps fixed rules apart from forecasts so a brief
# never presents a probability as if it were a requirement.
Basis = Literal["rule", "observation", "forecast"]


@dataclass
class Claim:
    text: str
    basis: Basis
    citations: list[Citation] = field(default_factory=list)


@dataclass
class RequiredAction:
    description: str
    target: str  # what to change: a rule id, file path, doc, or loan segment
    citations: list[Citation] = field(default_factory=list)


@dataclass
class ImpactBrief:
    """What an external change means, and what to do about it."""

    event: ChangeEvent
    summary: str
    affected_scope: list[str] = field(default_factory=list)
    claims: list[Claim] = field(default_factory=list)
    required_actions: list[RequiredAction] = field(default_factory=list)
    confidence: Confidence = "low"

    def uncited(self) -> list[str]:
        """Claims and actions with no citation — guardrail and eval hook."""
        missing = [c.text for c in self.claims if not c.citations]
        missing += [a.description for a in self.required_actions if not a.citations]
        return missing
