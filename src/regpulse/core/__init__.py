"""Domain-neutral core shared by RegPulse and (later) HazardLens.

Anything in here must not know about guides, bulletins, or climate data.
It defines the common contract: an external ChangeEvent comes in, an
ImpactBrief with Citations goes out, and both are scored by the same
eval runner. Regulatory-specific code lives outside this package.
"""

from .brief import Basis, Claim, Confidence, ImpactBrief, RequiredAction
from .citations import Citation
from .events import ChangeEvent

__all__ = [
    "Basis",
    "ChangeEvent",
    "Citation",
    "Claim",
    "Confidence",
    "ImpactBrief",
    "RequiredAction",
]
