"""Unit tests for the deterministic section diff."""

import pytest

from regpulse.diff import diff_sections, normalize
from regpulse.models import GuideSection


def s(sid, body, heading="H"):
    return GuideSection(section_id=sid, heading=heading, body=body)


def kinds(diffs):
    return [(d.section_id, d.change_type) for d in diffs]


def test_identical_guides_produce_no_diffs():
    sections = [s("A1", "x"), s("A2", "y")]
    assert diff_sections(sections, list(sections)) == []


def test_modified_body_keeps_original_text():
    old = [s("B3-6-02", "The maximum DTI ratio is 50%.")]
    new = [s("B3-6-02", "The maximum DTI ratio is 45%.")]
    [d] = diff_sections(old, new)
    assert d.change_type == "modified"
    assert d.old_text == "The maximum DTI ratio is 50%."
    assert d.new_text == "The maximum DTI ratio is 45%."


def test_heading_only_change_is_modified():
    assert kinds(diff_sections([s("A1", "x", "Old")], [s("A1", "x", "New")])) == [("A1", "modified")]


def test_added_and_removed():
    old = [s("A1", "x"), s("A2", "y")]
    new = [s("A1", "x"), s("A3", "z")]
    assert kinds(diff_sections(old, new)) == [("A3", "added"), ("A2", "removed")]


def test_order_new_guide_order_then_removed():
    old = [s("R1", "gone"), s("A1", "x"), s("A2", "y")]
    new = [s("A2", "y2"), s("N1", "n"), s("A1", "x2")]
    assert kinds(diff_sections(old, new)) == [
        ("A2", "modified"),
        ("N1", "added"),
        ("A1", "modified"),
        ("R1", "removed"),
    ]


@pytest.mark.parametrize(
    "old_body,new_body",
    [
        ("max LTV is\n97%", "max LTV is 97%"),  # PDF line wrap
        ("borrower’s income", "borrower's income"),  # smart quote
        ("120 days", "120 days"),  # non-breaking space
        ("self-em­ployed", "self-employed"),  # soft hyphen
        ("  padded  ", "padded"),
    ],
)
def test_extraction_noise_is_not_a_change(old_body, new_body):
    assert diff_sections([s("A1", old_body)], [s("A1", new_body)]) == []


def test_real_punctuation_change_is_detected():
    assert kinds(diff_sections([s("A1", "at least 2 years.")], [s("A1", "at least 2 years;")])) == [
        ("A1", "modified")
    ]


def test_duplicate_section_id_raises():
    with pytest.raises(ValueError, match="duplicate section_id 'A1' in new"):
        diff_sections([s("A1", "x")], [s("A1", "x"), s("A1", "y")])


def test_empty_inputs():
    assert diff_sections([], []) == []
    assert kinds(diff_sections([], [s("A1", "x")])) == [("A1", "added")]
    assert kinds(diff_sections([s("A1", "x")], [])) == [("A1", "removed")]


def test_normalize_collapses_whitespace():
    assert normalize(" a \n\t b ") == "a b"
