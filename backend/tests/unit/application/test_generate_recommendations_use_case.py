from __future__ import annotations

from datetime import datetime, timezone

from app.application.use_cases.generate_recommendations_use_case import (
    GenerateRecommendationsUseCase,
)
from app.domain.entities.evidence import Evidence
from app.domain.entities.score import CategoryScore, ScoreCard, ScoreCategory


def _make_scorecard(evidence_by_category: dict) -> ScoreCard:
    category_scores = {
        category: CategoryScore(category=category, raw_score=0.5, evidence=evidence)
        for category, evidence in evidence_by_category.items()
    }
    return ScoreCard(
        overall_score=50.0,
        category_scores=category_scores,
        weights_used={},
        generated_at=datetime.now(timezone.utc),
    )


def _failing_evidence(criterion: str, weight: float) -> Evidence:
    return Evidence(
        criterion=criterion,
        description=f"{criterion} description",
        found_value=False,
        expected_value=True,
        weight=weight,
        passed=False,
    )


def test_no_llm_provider_uses_template_fallback():
    scorecard = _make_scorecard(
        {ScoreCategory.SKILLS: [_failing_evidence("required_skill_present", 2.0)]}
    )
    use_case = GenerateRecommendationsUseCase(llm_provider=None)

    recommendations = use_case.execute(scorecard)

    assert len(recommendations) == 1
    assert recommendations[0].is_llm_generated is False
    assert "required_skill_present" in recommendations[0].message or (
        "description" in recommendations[0].message
    )


def test_llm_provider_used_when_available(fake_llm_provider):
    scorecard = _make_scorecard(
        {ScoreCategory.SKILLS: [_failing_evidence("required_skill_present", 2.0)]}
    )
    use_case = GenerateRecommendationsUseCase(llm_provider=fake_llm_provider)

    recommendations = use_case.execute(scorecard)

    assert recommendations[0].is_llm_generated is True
    assert recommendations[0].message == "LLM-generated recommendation."
    assert fake_llm_provider.suggest_calls == 1


def test_llm_failure_falls_back_to_template_never_raises(failing_llm_provider):
    scorecard = _make_scorecard(
        {ScoreCategory.SKILLS: [_failing_evidence("required_skill_present", 2.0)]}
    )
    use_case = GenerateRecommendationsUseCase(llm_provider=failing_llm_provider)

    # Must not raise, even though the LLM always fails.
    recommendations = use_case.execute(scorecard)

    assert len(recommendations) == 1
    assert recommendations[0].is_llm_generated is False


def test_only_failing_evidence_produces_recommendations():
    passing = Evidence(
        criterion="passed_check",
        description="ok",
        found_value=True,
        expected_value=True,
        weight=1.0,
        passed=True,
    )
    failing = _failing_evidence("failed_check", 1.0)
    scorecard = _make_scorecard({ScoreCategory.SKILLS: [passing, failing]})

    use_case = GenerateRecommendationsUseCase(llm_provider=None)
    recommendations = use_case.execute(scorecard)

    assert len(recommendations) == 1
    assert recommendations[0].criterion == "failed_check"


def test_prioritizes_highest_weight_evidence_first():
    scorecard = _make_scorecard(
        {
            ScoreCategory.SKILLS: [_failing_evidence("low_weight", 1.0)],
            ScoreCategory.EXPERIENCE: [_failing_evidence("high_weight", 3.0)],
        }
    )
    use_case = GenerateRecommendationsUseCase(llm_provider=None, max_recommendations=5)

    recommendations = use_case.execute(scorecard)

    assert recommendations[0].criterion == "high_weight"
    assert recommendations[1].criterion == "low_weight"


def test_max_recommendations_caps_output():
    evidence = [_failing_evidence(f"check_{i}", float(i)) for i in range(10)]
    scorecard = _make_scorecard({ScoreCategory.SKILLS: evidence})

    use_case = GenerateRecommendationsUseCase(llm_provider=None, max_recommendations=3)
    recommendations = use_case.execute(scorecard)

    assert len(recommendations) == 3
    # Highest weights (9, 8, 7) should be the ones kept.
    assert {r.criterion for r in recommendations} == {"check_9", "check_8", "check_7"}


def test_no_failing_evidence_returns_empty_list():
    passing = Evidence(
        criterion="ok",
        description="ok",
        found_value=True,
        expected_value=True,
        weight=1.0,
        passed=True,
    )
    scorecard = _make_scorecard({ScoreCategory.SKILLS: [passing]})
    use_case = GenerateRecommendationsUseCase(llm_provider=None)
    assert use_case.execute(scorecard) == []
