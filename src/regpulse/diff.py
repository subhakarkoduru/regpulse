"""Section-by-section diff of two guide versions.

Match sections by stable section_id; classify each as added / removed /
modified. Keep it deterministic and explainable — an LLM may summarize the
diff later, but the diff itself must not hallucinate changes.

Text is normalized before comparison so that re-extraction noise (PDF line
wraps, smart quotes, non-breaking spaces, soft hyphens) is never reported as
a regulatory change. The diff output keeps the original, un-normalized text.
"""

from __future__ import annotations

import re
import unicodedata

from .models import GuideSection, SectionDiff

_TRANSLATE = str.maketrans(
    {
        "‘": "'",
        "’": "'",
        "“": '"',
        "”": '"',
        "–": "-",
        "—": "-",
        "­": None,  # soft hyphen
    }
)
_WS = re.compile(r"\s+")


def normalize(text: str) -> str:
    """Canonical form used only for equality checks."""
    text = unicodedata.normalize("NFKC", text).translate(_TRANSLATE)
    return _WS.sub(" ", text).strip()


def _index(sections: list[GuideSection], label: str) -> dict[str, GuideSection]:
    index: dict[str, GuideSection] = {}
    for s in sections:
        if s.section_id in index:
            raise ValueError(f"duplicate section_id {s.section_id!r} in {label} sections")
        index[s.section_id] = s
    return index


def diff_sections(
    old: list[GuideSection], new: list[GuideSection]
) -> list[SectionDiff]:
    """Diff old guide sections against new guide sections.

    Output order: sections in new-guide order (added / modified), then
    removed sections in old-guide order. Unchanged sections are omitted.
    Raises ValueError on duplicate section ids — ambiguous input is a bug
    in extraction, not something to guess around.
    """
    old_idx = _index(old, "old")
    new_idx = _index(new, "new")
    diffs: list[SectionDiff] = []

    for sid, n in new_idx.items():
        o = old_idx.get(sid)
        if o is None:
            diffs.append(
                SectionDiff(sid, "added", new_heading=n.heading, new_text=n.body)
            )
        elif normalize(o.heading) != normalize(n.heading) or normalize(o.body) != normalize(n.body):
            diffs.append(
                SectionDiff(
                    sid,
                    "modified",
                    old_heading=o.heading,
                    new_heading=n.heading,
                    old_text=o.body,
                    new_text=n.body,
                )
            )

    for sid, o in old_idx.items():
        if sid not in new_idx:
            diffs.append(
                SectionDiff(sid, "removed", old_heading=o.heading, old_text=o.body)
            )

    return diffs
