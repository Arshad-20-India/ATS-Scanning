from __future__ import annotations

from app.application.use_cases.match_job_description_use_case import (
    MatchJobDescriptionUseCase,
)
from app.domain.services.category_scorers import SkillsScorer
from app.domain.services.scoring_engine import ScoringEngine
from app.domain.services.scoring_policy import ScoringPolicy


def test_execute_returns_scorecard(fixed_resume, fixed_job_description):
    engine = ScoringEngine(
        scorers=[SkillsScorer()],
        policy=ScoringPolicy(weights={SkillsScorer.category: 1.0}),
    )
    use_case = MatchJobDescriptionUseCase(scoring_engine=engine)

    scorecard = use_case.execute(fixed_resume, fixed_job_description)

    assert 0.0 <= scorecard.overall_score <= 100.0
    assert SkillsScorer.category in scorecard.category_scores


def test_does_not_mutate_inputs(fixed_resume, fixed_job_description):
    engine = ScoringEngine(
        scorers=[SkillsScorer()],
        policy=ScoringPolicy(weights={SkillsScorer.category: 1.0}),
    )
    use_case = MatchJobDescriptionUseCase(scoring_engine=engine)

    original_skill_count = len(fixed_resume.skills)
    use_case.execute(fixed_resume, fixed_job_description)

    assert len(fixed_resume.skills) == original_skill_count
