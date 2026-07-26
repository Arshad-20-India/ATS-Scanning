from __future__ import annotations

from app.infrastructure.llm.response_validator import (
    extract_allowed_numbers,
    find_ungrounded_numbers,
    is_grounded,
)


def test_grounded_response_passes(sample_evidence_list):
    response = "You're missing Kubernetes and have 3.2 years of the 5.0 required."
    assert is_grounded(response, sample_evidence_list) is True


def test_fabricated_number_fails(sample_evidence_list):
    response = "You have 3.2 years of experience but the role needs 10 years."
    assert is_grounded(response, sample_evidence_list) is False
    assert "10" in find_ungrounded_numbers(response, sample_evidence_list)


def test_ratio_and_percentage_equivalence_recognized():
    from app.domain.entities.evidence import Evidence

    evidence = [
        Evidence(
            criterion="passive_voice_ratio",
            description="x",
            found_value=0.4,
            expected_value="<= 0.15",
            weight=1.0,
            passed=False,
        )
    ]
    # "40%" is the same fact as found_value=0.4 -- must be recognized as grounded.
    response = "About 40% of your bullets use passive voice."
    assert is_grounded(response, evidence) is True


def test_benign_small_numbers_do_not_trigger_false_positive(sample_evidence_list):
    response = "Here are 2 things to improve: first, Kubernetes; second, experience."
    assert is_grounded(response, sample_evidence_list) is True


def test_extract_allowed_numbers_includes_benign_defaults():
    allowed = extract_allowed_numbers([])
    assert {"0", "1", "2", "3"} <= allowed


def test_empty_response_is_trivially_grounded(sample_evidence_list):
    assert is_grounded("", sample_evidence_list) is True
