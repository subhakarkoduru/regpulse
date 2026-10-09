"""RegPulse golden-case evals, run on the shared core runner.

Each case in evals/golden/*.json:
  {"name", "kind": "section_diff", "old_sections", "new_sections", "expected_diffs"}
("kind" defaults to "section_diff".)

Run: python -m regpulse.eval [--golden-dir PATH]
"""

from __future__ import annotations

import argparse
from pathlib import Path

from .core import evals
from .diff import diff_sections
from .models import GuideSection

DEFAULT_GOLDEN_DIR = Path(__file__).resolve().parent.parent.parent / "evals" / "golden"


def _sections(raw: list[dict]) -> list[GuideSection]:
    return [GuideSection(**s) for s in raw]


@evals.register("section_diff")
def eval_section_diff(case: dict) -> list[str]:
    actual = {
        d.section_id: d.change_type
        for d in diff_sections(_sections(case["old_sections"]), _sections(case["new_sections"]))
    }
    expected = {d["section_id"]: d["change_type"] for d in case["expected_diffs"]}

    failures = []
    for sid, ct in expected.items():
        if sid not in actual:
            failures.append(f"missed {sid} ({ct})")
        elif actual[sid] != ct:
            failures.append(f"{sid}: expected {ct}, got {actual[sid]}")
    for sid, ct in actual.items():
        if sid not in expected:
            failures.append(f"spurious {sid} ({ct})")
    return failures


def run_eval(golden_dir: Path = DEFAULT_GOLDEN_DIR) -> bool:
    """Run all golden cases. Returns True if all pass. Prints a summary."""
    cases = evals.load_cases(golden_dir)
    if not cases:
        print(f"No golden cases found in {golden_dir}")
        return True
    return evals.report(evals.run_cases(cases, default_kind="section_diff"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--golden-dir", type=Path, default=DEFAULT_GOLDEN_DIR)
    args = parser.parse_args()
    raise SystemExit(0 if run_eval(args.golden_dir) else 1)
