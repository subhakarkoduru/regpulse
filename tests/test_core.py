"""Tests for the domain-neutral core shared with HazardLens."""

import json
from datetime import date

import pytest

from regpulse.core import ChangeEvent, Citation, Claim, ImpactBrief, RequiredAction
from regpulse.core import evals
from regpulse.eval import run_eval
from regpulse.models import Bulletin


def test_bulletin_is_a_change_event():
    b = Bulletin(
        event_id="SEL-2026-07",
        source="Fannie Mae Selling Guide",
        title="Selling Guide Announcement",
        published=date(2026, 7, 1),
        url="https://example.org",
    )
    assert isinstance(b, ChangeEvent)
    assert b.kind == "regulatory"
    assert b.affected_section_ids == []


def test_citation_requires_source_and_locator():
    with pytest.raises(ValueError):
        Citation(source="", locator="B3-6-02", url="u")


def test_brief_reports_uncited_claims_and_actions():
    cite = Citation(source="Fannie Mae Selling Guide", locator="B3-6-02", url="u")
    event = ChangeEvent(event_id="e", source="s", kind="climate", title="t", published=None, url="u")
    brief = ImpactBrief(
        event=event,
        summary="s",
        claims=[
            Claim("DTI cap is 45%", basis="rule", citations=[cite]),
            Claim("Wetter than normal winter", basis="forecast"),
        ],
        required_actions=[RequiredAction("Update DTI rule", target="rules/dti.yaml")],
    )
    assert brief.uncited() == ["Wetter than normal winter", "Update DTI rule"]


def _write(tmp_path, name, case):
    (tmp_path / name).write_text(json.dumps(case))


def test_section_diff_eval_pass_and_fail(tmp_path, capsys):
    base = {
        "old_sections": [{"section_id": "B3-6-02", "heading": "DTI", "body": "max 50%"}],
        "new_sections": [{"section_id": "B3-6-02", "heading": "DTI", "body": "max 45%"}],
    }
    _write(tmp_path, "01.json", {**base, "name": "good", "expected_diffs": [{"section_id": "B3-6-02", "change_type": "modified"}]})
    assert run_eval(tmp_path) is True

    _write(tmp_path, "02.json", {**base, "name": "bad", "expected_diffs": []})
    assert run_eval(tmp_path) is False
    assert "spurious B3-6-02 (modified)" in capsys.readouterr().out


def test_unknown_kind_fails_without_crashing(tmp_path):
    results = evals.run_cases([("x.json", {"kind": "climate_brief"})], default_kind="section_diff")
    assert not results[0].passed
    assert "no evaluator" in results[0].failures[0]


def test_crashing_evaluator_is_a_failure_not_a_crash():
    results = evals.run_cases([("x.json", {"name": "broken"})], default_kind="section_diff")
    assert not results[0].passed  # missing keys -> KeyError captured


def test_empty_golden_dir_passes(tmp_path):
    assert run_eval(tmp_path) is True
