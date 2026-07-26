from __future__ import annotations

import pytest

from app.domain.entities.evidence import Evidence
from app.domain.entities.score import CategoryScore, ScoreCategory
from app.domain.services.scoring_policy import ScoringPolicy


def test_rejects_weights_that_dont_sum_to_one():
    with pytest.raises(ValueError, match="must sum to 1.0"):
        ScoringPolicy(
            weights={
                ScoreCategory.SKILLS: 0.5,
                ScoreCategory.EXPERIENCE: 0.6,
            }
        )


def test_rejects_negative_weight():
    with pytest.raises(ValueError, match=">= 0"):
        ScoringPolicy(weights={ScoreCategory.SKILLS: -0.1, ScoreCategory.EXPERIENCE: 1.1})


def test_rejects_empty_weights():
    with pytest.raises(ValueError):
        ScoringPolicy(weights={})


def test_accepts_weights_within_rounding_tolerance():
    # 0.333 * 3 = 0.999, should be tolerated
    policy = ScoringPolicy(
        weights={
            ScoreCategory.SKILLS: 0.333,
            ScoreCategory.EXPERIENCE: 0.333,
            ScoreCategory.EDUCATION: 0.333,
        }
    )
    assert policy.weights[ScoreCategory.SKILLS] == 0.333


def test_compute_overall_weighted_sum():
    policy = ScoringPolicy(
        weights={ScoreCategory.SKILLS: 0.6, ScoreCategory.EXPERIENCE: 0.4}
    )
    scores = {
        ScoreCategory.SKILLS: CategoryScore(category=ScoreCategory.SKILLS, raw_score=1.0),
        ScoreCategory.EXPERIENCE: CategoryScore(
            category=ScoreCategory.EXPERIENCE, raw_score=0.5
        ),
    }
    # 1.0*0.6 + 0.5*0.4 = 0.8 -> 80.0
    assert policy.compute_overall(scores) == 80.0


def test_compute_overall_ignores_missing_category_without_redistributing_weight():
    policy = ScoringPolicy(
        weights={ScoreCategory.SKILLS: 0.6, ScoreCategory.EXPERIENCE: 0.4}
    )
    scores = {
        ScoreCategory.SKILLS: CategoryScore(category=ScoreCategory.SKILLS, raw_score=1.0),
        # EXPERIENCE missing entirely
    }
    # Only SKILLS contributes: 1.0 * 0.6 = 0.6 -> 60.0 (NOT 100.0)
    assert policy.compute_overall(scores) == 60.0


def test_weights_property_returns_a_copy_not_internal_reference():
    policy = ScoringPolicy(
        weights={ScoreCategory.SKILLS: 0.6, ScoreCategory.EXPERIENCE: 0.4}
    )
    weights = policy.weights
    weights[ScoreCategory.SKILLS] = 999
    assert policy.weights[ScoreCategory.SKILLS] == 0.6
