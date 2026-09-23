"""Section-by-section diff of two guide versions.

Match sections by stable section_id; classify each as added / removed /
modified. Keep it deterministic and explainable — an LLM may summarize the
diff later, but the diff itself must not hallucinate changes.
"""

from __future__ import annotations

from .models import GuideSection, SectionDiff


def diff_sections(
    old: list[GuideSection], new: list[GuideSection]
) -> list[SectionDiff]:
    """Diff old guide sections against new guide sections."""
    raise NotImplementedError("Week 1, step 3: implement deterministic section diff")
