"""
ScoringPolicy owns exactly one thing: how category scores combine into
an overall 0-100 number. This is deliberately isolated from the
scorers themselves so the *weighting* can be changed (e.g. per
industry, per company config) without touching how any individual
category is evaluated.

Weights are configuration, not code, and are always exposed on the
final ScoreCard (`weights_used`) so a user can see exactly how much
each category counted.
"""

from __future__ import annotations

import math
from typing import Dict, Optional

from app.domain.entities.score import CategoryScore, ScoreCategory

DEFAULT_WEIGHTS: Dict[ScoreCategory, float] = {
    ScoreCategory.SEMANTIC_ALIGNMENT: 0.30,   # Keyword Match (30%)
    ScoreCategory.SKILLS: 0.20,               # Skills Match (20%)
    ScoreCategory.EXPERIENCE: 0.15,           # Experience Match (15%)
    ScoreCategory.EDUCATION: 0.10,            # Education (10%)
    ScoreCategory.ATS_COMPATIBILITY: 0.10,    # Formatting (10%)
    ScoreCategory.GRAMMAR: 0.05,              # Action Verbs (5%)
    ScoreCategory.PROJECTS: 0.05,             # Readability (5%)
    ScoreCategory.CERTIFICATIONS: 0.05,       # Missing Requirements (5%)
}


class ScoringPolicy:
    def __init__(self, weights: Optional[Dict[ScoreCategory, float]] = None) -> None:
        self._weights = dict(weights) if weights is not None else dict(DEFAULT_WEIGHTS)
        self._validate()

    def _validate(self) -> None:
        if not self._weights:
            raise ValueError("ScoringPolicy requires at least one category weight")
        for category, weight in self._weights.items():
            if weight < 0:
                raise ValueError(
                    f"Weight for {category} must be >= 0, got {weight}"
                )
        total = sum(self._weights.values())
        if not math.isclose(total, 1.0, abs_tol=0.01):
            raise ValueError(
                f"Category weights must sum to 1.0 (+/- 0.01), got {total:.4f}. "
                f"Weights: {self._weights}"
            )

    @property
    def weights(self) -> Dict[ScoreCategory, float]:
        return dict(self._weights)

    def compute_overall(
        self, category_scores: Dict[ScoreCategory, CategoryScore]
    ) -> float:
        """
        Overall score is a documented weighted sum over categories that
        were actually evaluated. If a category is missing from
        `category_scores` (e.g. a scorer was intentionally excluded for
        this run), its weight is simply not applied — it does not
        silently count as zero, and it does not get its weight
        redistributed to other categories (that would be an implicit,
        undocumented policy change).
        """
        overall = 0.0
        for category, weight in self._weights.items():
            category_score = category_scores.get(category)
            if category_score is None:
                continue
            overall += category_score.raw_score * weight
        return round(overall * 100, 1)
