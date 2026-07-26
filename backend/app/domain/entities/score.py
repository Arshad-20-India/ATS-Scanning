from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List

from app.domain.entities.evidence import Evidence


class ScoreCategory(str, Enum):
    SKILLS = "skills"
    EXPERIENCE = "experience"
    EDUCATION = "education"
    PROJECTS = "projects"
    CERTIFICATIONS = "certifications"
    GRAMMAR = "grammar"
    ATS_COMPATIBILITY = "ats_compatibility"
    SEMANTIC_ALIGNMENT = "semantic_alignment"


@dataclass(frozen=True)
class CategoryScore:
    """
    The result of evaluating one category (skills, experience, ...).

    `raw_score` is always normalized to [0, 1] so categories are
    comparable before weighting. It is *derived*, not asserted: it is
    always the ratio of achieved evidence weight to total evidence
    weight (see ICategoryScorer implementations) — there is no code
    path that sets raw_score directly to an arbitrary number.
    """

    category: ScoreCategory
    raw_score: float  # normalized 0..1
    evidence: List[Evidence] = field(default_factory=list)
    weight_in_overall: float = 0.0  # filled in by ScoringPolicy/ScoringEngine

    def __post_init__(self) -> None:
        if not (0.0 <= self.raw_score <= 1.0):
            raise ValueError(
                f"CategoryScore.raw_score must be in [0, 1], got {self.raw_score}"
            )

    @property
    def score_percent(self) -> float:
        return round(self.raw_score * 100, 1)

    @property
    def weighted_contribution(self) -> float:
        """Contribution of this category to the overall 0-100 score."""
        return round(self.raw_score * self.weight_in_overall * 100, 2)

    @property
    def failed_evidence(self) -> List[Evidence]:
        return [e for e in self.evidence if not e.passed]

    @property
    def passed_evidence(self) -> List[Evidence]:
        return [e for e in self.evidence if e.passed]


@dataclass(frozen=True)
class ScoreCard:
    """
    Top-level, immutable result of a full resume-vs-JD evaluation.
    This is the object that gets serialized to the API response and
    persisted for audit/history purposes.
    """

    overall_score: float  # 0..100
    category_scores: Dict[ScoreCategory, CategoryScore]
    weights_used: Dict[ScoreCategory, float]
    generated_at: datetime

    def evidence_for(self, category: ScoreCategory) -> List[Evidence]:
        cs = self.category_scores.get(category)
        return cs.evidence if cs else []

    def all_failed_evidence(self) -> List[Evidence]:
        failed = []
        for cs in self.category_scores.values():
            failed.extend(cs.failed_evidence)
        return failed

    def to_summary_dict(self) -> dict:
        """Lightweight summary, useful for logging/quick display."""
        return {
            "overall_score": self.overall_score,
            "categories": {
                cat.value: cs.score_percent
                for cat, cs in self.category_scores.items()
            },
            "generated_at": self.generated_at.isoformat(),
        }
