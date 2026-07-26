from __future__ import annotations

from app.infrastructure.persistence.mappers import (
    job_description_from_dict,
    job_description_to_dict,
    recommendations_from_list,
    recommendations_to_list,
    resume_from_dict,
    resume_to_dict,
    scorecard_from_dict,
    scorecard_to_dict,
)


def test_resume_round_trip_preserves_all_fields(full_resume):
    data = resume_to_dict(full_resume)
    reconstructed = resume_from_dict(data)

    assert reconstructed == full_resume


def test_resume_round_trip_with_no_optional_fields():
    from app.domain.entities.resume import ContactInfo, Resume

    minimal = Resume(raw_text="minimal", contact_info=ContactInfo())
    data = resume_to_dict(minimal)
    reconstructed = resume_from_dict(data)

    assert reconstructed == minimal
    assert reconstructed.writing_metrics is None


def test_job_description_round_trip_preserves_all_fields(full_job_description):
    data = job_description_to_dict(full_job_description)
    reconstructed = job_description_from_dict(data)

    assert reconstructed == full_job_description


def test_job_description_round_trip_with_defaults():
    from app.domain.entities.job_description import JobDescription

    minimal = JobDescription(raw_text="x", title="Engineer")
    data = job_description_to_dict(minimal)
    reconstructed = job_description_from_dict(data)

    assert reconstructed == minimal


def test_scorecard_round_trip_preserves_evidence_and_scores():
    from datetime import datetime, timezone

    from app.domain.entities.evidence import Evidence
    from app.domain.entities.score import CategoryScore, ScoreCard, ScoreCategory

    original = ScoreCard(
        overall_score=87.5,
        category_scores={
            ScoreCategory.SKILLS: CategoryScore(
                category=ScoreCategory.SKILLS,
                raw_score=0.9,
                weight_in_overall=0.3,
                evidence=[
                    Evidence(
                        criterion="required_skill_present",
                        description="Python found",
                        found_value=True,
                        expected_value=True,
                        weight=2.0,
                        passed=True,
                        confidence=1.0,
                        source_span="Skills section",
                    )
                ],
            )
        },
        weights_used={ScoreCategory.SKILLS: 0.3},
        generated_at=datetime(2026, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
    )

    data = scorecard_to_dict(original)
    reconstructed = scorecard_from_dict(data)

    assert reconstructed == original


def test_scorecard_round_trip_preserves_falsy_and_none_evidence_values():
    """
    Regression guard: found_value=False or found_value=0 must not be
    lost/coerced during JSON round-trip (a naive `if value` check
    elsewhere would treat these as missing).
    """
    from datetime import datetime, timezone

    from app.domain.entities.evidence import Evidence
    from app.domain.entities.score import CategoryScore, ScoreCard, ScoreCategory

    original = ScoreCard(
        overall_score=0.0,
        category_scores={
            ScoreCategory.SKILLS: CategoryScore(
                category=ScoreCategory.SKILLS,
                raw_score=0.0,
                evidence=[
                    Evidence(
                        criterion="c",
                        description="d",
                        found_value=False,
                        expected_value=True,
                        weight=1.0,
                        passed=False,
                        confidence=0.0,
                        source_span=None,
                    )
                ],
            )
        },
        weights_used={},
        generated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )

    reconstructed = scorecard_from_dict(scorecard_to_dict(original))
    evidence = reconstructed.category_scores[ScoreCategory.SKILLS].evidence[0]

    assert evidence.found_value is False
    assert evidence.confidence == 0.0
    assert evidence.source_span is None


def test_recommendations_round_trip():
    from app.application.dto import Recommendation
    from app.domain.entities.score import ScoreCategory

    original = [
        Recommendation(
            criterion="required_skill_present",
            category=ScoreCategory.SKILLS,
            message="Add Kubernetes",
            is_llm_generated=True,
        )
    ]

    reconstructed = recommendations_from_list(recommendations_to_list(original))
    assert reconstructed == original
