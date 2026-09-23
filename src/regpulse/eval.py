"""Golden-case eval harness for the diff pipeline.

Each case in evals/golden/*.json: {old_sections, new_sections, expected_diffs}.
Run: python -m regpulse.eval
"""

from __future__ import annotations

import json
from pathlib import Path

from .diff import diff_sections
from .models import GuideSection

GOLDEN_DIR = Path(__file__).resolve().parent.parent.parent / "evals" / "golden"


def load_cases() -> list[dict]:
    cases = []
    for path in sorted(GOLDEN_DIR.glob("*.json")):
        cases.append((path.name, json.loads(path.read_text())))
    return cases


def run_eval() -> bool:
    """Run all golden cases. Returns True if all pass. Prints a summary."""
    raise NotImplementedError("Week 1, step 4: implement harness alongside first cases")


if __name__ == "__main__":
    ok = run_eval()
    raise SystemExit(0 if ok else 1)
