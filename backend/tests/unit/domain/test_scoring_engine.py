from __future__ import annotations

import pytest

from app.domain.entities.score import ScoreCategory
from app.domain.services.category_scorers.ats_scorer import ATSScorer
from app.domain.services.category_scorers.certifications_scorer import (
    CertificationsScorer,
)
from app.domain.services.category_scorers.education_scorer import EducationScorer
from app.domain.services.category_scorers.experience_scorer import ExperienceScorer
from app.domain.services.category_scorers.grammar_scorer import GrammarScorer
from app.domain.services.category_scorers.projects_scorer import ProjectsScorer
from app.domain.services.category_scorers.skills_scorer import SkillsScorer
from app.domain.services.matching_policy import MatchingPolicy
from app.domain.services.scoring_engine import ScoringEngine
from app.domain.services.scoring_policy import ScoringPolicy


def _build_full_engine(fake_embedder) -> ScoringEngine:
    matching_policy = MatchingPolicy(embedder=fake_embedder, similarity_threshold=0.3)
    scorers = [
        SkillsScorer(),
        ExperienceScorer(matching_policy=matching_policy),
        EducationScorer(),
        ProjectsScorer(),
        CertificationsScorer(),
        GrammarScorer(),
        ATSScorer(),
    ]
    return ScoringEngine(scorers=scorers, policy=ScoringPolicy())


def test_engine_produces_full_scorecard(sample_resume, sample_job_description, fake_embedder):
    engine = _build_full_engine(fake_embedder)
    scorecard = engine.evaluate(sample_resume, sample_job_description)

    assert 0.0 <= scorecard.overall_score <= 100.0
    assert set(scorecard.category_scores.keys()) == {
        ScoreCategory.SKILLS,
        ScoreCategory.EXPERIENCE,
        ScoreCategory.EDUCATION,
        ScoreCategory.PROJECTS,
        ScoreCategory.CERTIFICATIONS,
        ScoreCategory.GRAMMAR,
        ScoreCategory.ATS_COMPATIBILITY,
    }
    # Every category score must carry evidence -- no bare numbers.
    for category_score in scorecard.category_scores.values():
        assert len(category_score.evidence) > 0


def test_engine_rejects_empty_scorer_list():
    with pytest.raises(ValueError, match="at least one category scorer"):
        ScoringEngine(scorers=[], policy=ScoringPolicy())


def test_weights_used_are_recorded_on_scorecard(
    sample_resume, sample_job_description, fake_embedder
):
    engine = _build_full_engine(fake_embedder)
    scorecard = engine.evaluate(sample_resume, sample_job_description)
    assert scorecard.weights_used[ScoreCategory.SKILLS] == 0.30


def test_scorecard_can_report_all_failed_evidence(
    sample_resume, sample_job_description, fake_embedder
):
    engine = _build_full_engine(fake_embedder)
    scorecard = engine.evaluate(sample_resume, sample_job_description)

    failed = scorecard.all_failed_evidence()
    # Preferred skill "Kubernetes" is not on the resume -> should surface as failed evidence.
    assert any("Kubernetes" in e.description for e in failed)


def test_partial_scorer_selection_only_scores_included_categories(
    sample_resume, sample_job_description
):
    # Only run Skills + ATS -- overall score should only reflect those two,
    # per ScoringPolicy's "no redistribution" rule.
    scorers = [SkillsScorer(), ATSScorer()]
    engine = ScoringEngine(scorers=scorers, policy=ScoringPolicy())
    scorecard = engine.evaluate(sample_resume, sample_job_description)

    assert set(scorecard.category_scores.keys()) == {
        ScoreCategory.SKILLS,
        ScoreCategory.ATS_COMPATIBILITY,
    }
    # weight for skills(0.30) + ats(0.10) = 0.40 of total possible weight was evaluated
    max_possible = (0.30 + 0.10) * 100
    assert scorecard.overall_score <= max_possible + 0.1
