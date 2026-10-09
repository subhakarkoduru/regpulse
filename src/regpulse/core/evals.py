"""Generic golden-case eval runner.

Each golden case is a JSON file with a "kind" field. Projects register an
evaluator per kind; the runner loads every case, dispatches it, and reports.
RegPulse registers "section_diff"; HazardLens will register its own kinds.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

# An evaluator takes a case dict and returns a list of failure messages
# (empty list = pass).
Evaluator = Callable[[dict], list[str]]

_REGISTRY: dict[str, Evaluator] = {}


def register(kind: str) -> Callable[[Evaluator], Evaluator]:
    def deco(fn: Evaluator) -> Evaluator:
        if kind in _REGISTRY and _REGISTRY[kind] is not fn:
            raise ValueError(f"evaluator for kind {kind!r} already registered")
        _REGISTRY[kind] = fn
        return fn

    return deco


@dataclass
class CaseResult:
    name: str
    kind: str
    failures: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not self.failures


def load_cases(directory: Path) -> list[tuple[str, dict]]:
    return [(p.name, json.loads(p.read_text())) for p in sorted(directory.glob("*.json"))]


def run_cases(cases: list[tuple[str, dict]], default_kind: str) -> list[CaseResult]:
    results = []
    for filename, case in cases:
        kind = case.get("kind", default_kind)
        name = case.get("name", filename)
        evaluator = _REGISTRY.get(kind)
        if evaluator is None:
            results.append(CaseResult(name, kind, [f"no evaluator registered for kind {kind!r}"]))
            continue
        try:
            failures = evaluator(case)
        except Exception as exc:  # a crashing case is a failing case, not a crashed run
            failures = [f"{type(exc).__name__}: {exc}"]
        results.append(CaseResult(name, kind, failures))
    return results


def report(results: list[CaseResult]) -> bool:
    for r in results:
        print(f"{'PASS' if r.passed else 'FAIL'}  [{r.kind}] {r.name}")
        for f in r.failures:
            print(f"      - {f}")
    passed = sum(r.passed for r in results)
    print(f"\n{passed}/{len(results)} cases passed")
    return passed == len(results)
