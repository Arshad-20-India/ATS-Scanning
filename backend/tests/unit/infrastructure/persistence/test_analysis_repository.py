from __future__ import annotations

from datetime import datetime, timezone

from app.application.dto import AnalysisResult, Recommendation
from app.domain.entities.score import CategoryScore, ScoreCard, ScoreCategory
from app.infrastructure.persistence.analysis_repository import (
    SQLAlchemyAnalysisRepository,
)
from app.infrastructure.persistence.job_description_repository import (
    SQLAlchemyJobDescriptionRepository,
)
from app.infrastructure.persistence.resume_repository import SQLAlchemyResumeRepository


def _build_analysis_result(full_resume, full_job_description) -> AnalysisResult:
    scorecard = ScoreCard(
        overall_score=82.0,
        category_scores={
            ScoreCategory.SKILLS: CategoryScore(
                category=ScoreCategory.SKILLS, raw_score=0.9, weight_in_overall=0.3
            )
        },
        weights_used={ScoreCategory.SKILLS: 0.3},
        generated_at=datetime(2026, 1, 1, tzinfo=timezone.utc),
    )
    recommendations = [
        Recommendation(
            criterion="preferred_skill_present",
            category=ScoreCategory.SKILLS,
            message="Add Kubernetes",
            is_llm_generated=False,
        )
    ]
    return AnalysisResult(
        resume=full_resume,
        job_description=full_job_description,
        scorecard=scorecard,
        recommendations=recommendations,
    )


def test_save_requires_real_resume_and_jd_foreign_keys(
    db_session, full_resume, full_job_description
):
    """
    This is the test that actually proves the FK relationships are
    correctly declared: saving an analysis against IDs that don't
    exist in resumes/job_descriptions should fail at the DB level
    (constraint violation), and saving against real IDs should succeed.
    """
    resume_record = SQLAlchemyResumeRepository(db_session).save(
        full_resume, filename="r.pdf"
    )
    jd_record = SQLAlchemyJobDescriptionRepository(db_session).save(full_job_description)

    repo = SQLAlchemyAnalysisRepository(db_session)
    analysis_result = _build_analysis_result(full_resume, full_job_description)

    record = repo.save(
        analysis_result,
        resume_id=resume_record.id,
        job_description_id=jd_record.id,
    )

    assert record.resume_id == resume_record.id
    assert record.job_description_id == jd_record.id
    assert record.scorecard.overall_score == 82.0


def test_save_with_nonexistent_foreign_key_raises(db_session, full_resume, full_job_description):
    import pytest
    from sqlalchemy.exc import IntegrityError

    repo = SQLAlchemyAnalysisRepository(db_session)
    analysis_result = _build_analysis_result(full_resume, full_job_description)

    with pytest.raises(IntegrityError):
        repo.save(
            analysis_result,
            resume_id="00000000-0000-0000-0000-000000000000",
            job_description_id="00000000-0000-0000-0000-000000000000",
        )
    db_session.rollback()


def test_get_by_id_reconstructs_scorecard_and_recommendations(
    db_session, full_resume, full_job_description
):
    resume_record = SQLAlchemyResumeRepository(db_session).save(
        full_resume, filename="r.pdf"
    )
    jd_record = SQLAlchemyJobDescriptionRepository(db_session).save(full_job_description)

    repo = SQLAlchemyAnalysisRepository(db_session)
    analysis_result = _build_analysis_result(full_resume, full_job_description)
    saved = repo.save(
        analysis_result, resume_id=resume_record.id, job_description_id=jd_record.id
    )

    fetched = repo.get_by_id(saved.id)

    assert fetched is not None
    assert fetched.scorecard.overall_score == 82.0
    assert fetched.recommendations[0].message == "Add Kubernetes"


def test_list_by_user_returns_all_their_analyses(
    db_session, full_resume, full_job_description, make_test_user
):
    resume_record = SQLAlchemyResumeRepository(db_session).save(
        full_resume, filename="r.pdf"
    )
    jd_record = SQLAlchemyJobDescriptionRepository(db_session).save(full_job_description)

    repo = SQLAlchemyAnalysisRepository(db_session)
    analysis_result = _build_analysis_result(full_resume, full_job_description)
    user = make_test_user()

    repo.save(
        analysis_result,
        resume_id=resume_record.id,
        job_description_id=jd_record.id,
        user_id=user,
    )
    repo.save(
        analysis_result,
        resume_id=resume_record.id,
        job_description_id=jd_record.id,
        user_id=user,
    )

    results = repo.list_by_user(user)
    assert len(results) == 2
