"""
Common contract for every category scorer, plus a single shared
aggregation function.

Enforcing one aggregation function (`aggregate_evidence`) across all
scorers is what guarantees the "no arbitrary scores" principle holds
structurally rather than by convention: a raw_score is *always*
(achieved weight) / (total weight) over an Evidence list. A scorer
cannot compute raw_score any other way without deviating from this
shared helper, which makes such deviations easy to spot in review.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List

from app.domain.entities.evidence import Evidence
from app.domain.entities.job_description import JobDescription
from app.domain.entities.resume import Resume
from app.domain.entities.score import CategoryScore, ScoreCategory


def aggregate_evidence(
    category: ScoreCategory, evidence: List[Evidence]
) -> CategoryScore:
    """
    Reduce an Evidence list to a normalized CategoryScore.

    raw_score = sum(weight for passed evidence) / sum(weight for all evidence)

    If there is no evidence at all (e.g. a JD specified zero
    requirements for this category), the category is scored as a
    perfect pass with an explanatory evidence entry rather than
    dividing by zero or silently scoring 0 — absence of a requirement
    is not the same as failing one.
    """
    if not evidence:
        return CategoryScore(
            category=category,
            raw_score=1.0,
            evidence=[
                Evidence(
                    criterion="no_requirements_specified",
                    description=(
                        f"The job description specified no {category.value} "
                        f"requirements to evaluate against."
                    ),
                    found_value=None,
                    expected_value=None,
                    weight=0.0,
                    passed=True,
                    confidence=1.0,
                )
            ],
        )

    total_weight = sum(e.weight for e in evidence)
    if total_weight == 0:
        # All evidence items were informational (weight=0); treat as pass.
        raw_score = 1.0
    else:
        achieved_weight = sum(e.weight for e in evidence if e.passed)
        raw_score = achieved_weight / total_weight

    return CategoryScore(category=category, raw_score=raw_score, evidence=evidence)


class ICategoryScorer(ABC):
    category: ScoreCategory

    @abstractmethod
    def score(self, resume: Resume, job_description: JobDescription) -> CategoryScore:
        raise NotImplementedError
