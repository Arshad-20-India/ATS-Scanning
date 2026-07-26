"""
Application-layer output shapes.

These are thin wrappers around domain entities, not parallel/duplicate
models (see backend/README.md's "no duplicate entity models" rule).
`AnalysisResult` bundles a Resume, JobDescription, ScoreCard, and
Recommendations into the one object the API layer (Phase 6) will
serialize -- but every field on it is either a domain entity or a
direct derivative of one.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from app.domain.entities.job_description import JobDescription
from app.domain.entities.resume import Resume
from app.domain.entities.score import ScoreCard, ScoreCategory


@dataclass(frozen=True)
class Recommendation:
    """
    One actionable recommendation, always traceable back to the
    specific Evidence.criterion that produced it -- the application
    layer's continuation of Phase 1's "no score/claim without
    evidence" rule.
    """

    criterion: str
    category: ScoreCategory
    message: str
    is_llm_generated: bool


@dataclass(frozen=True)
class AnalysisResult:
    resume: Resume
    job_description: JobDescription
    scorecard: ScoreCard
    recommendations: List[Recommendation]
