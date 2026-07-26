"""
Analysis schemas. EvidenceSchema is the API-layer continuation of the
platform's core rule: every score the frontend receives comes bundled
with the Evidence that produced it (see app/domain/entities/evidence.py
docstring). Nothing here summarizes evidence away.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel

from app.application.dto import AnalysisResult, Recommendation
from app.domain.entities.evidence import Evidence
from app.domain.entities.score import CategoryScore, ScoreCard


class AnalyzeRequest(BaseModel):
    job_description_text: str


class EvidenceSchema(BaseModel):
    criterion: str
    description: str
    found_value: Any
    expected_value: Any
    weight: float
    passed: bool
    confidence: float
    source_span: Optional[str]

    @classmethod
    def from_domain(cls, evidence: Evidence) -> "EvidenceSchema":
        return cls(
            criterion=evidence.criterion,
            description=evidence.description,
            found_value=evidence.found_value,
            expected_value=evidence.expected_value,
            weight=evidence.weight,
            passed=evidence.passed,
            confidence=evidence.confidence,
            source_span=evidence.source_span,
        )


class CategoryScoreSchema(BaseModel):
    category: str
    score_percent: float
    weighted_contribution: float
    evidence: List[EvidenceSchema]

    @classmethod
    def from_domain(cls, category_score: CategoryScore) -> "CategoryScoreSchema":
        return cls(
            category=category_score.category.value,
            score_percent=category_score.score_percent,
            weighted_contribution=category_score.weighted_contribution,
            evidence=[EvidenceSchema.from_domain(e) for e in category_score.evidence],
        )


class ScoreCardSchema(BaseModel):
    overall_score: float
    category_scores: List[CategoryScoreSchema]
    generated_at: datetime

    @classmethod
    def from_domain(cls, scorecard: ScoreCard) -> "ScoreCardSchema":
        return cls(
            overall_score=scorecard.overall_score,
            category_scores=[
                CategoryScoreSchema.from_domain(cs)
                for cs in scorecard.category_scores.values()
            ],
            generated_at=scorecard.generated_at,
        )


class RecommendationSchema(BaseModel):
    criterion: str
    category: str
    message: str
    is_llm_generated: bool

    @classmethod
    def from_domain(cls, recommendation: Recommendation) -> "RecommendationSchema":
        return cls(
            criterion=recommendation.criterion,
            category=recommendation.category.value,
            message=recommendation.message,
            is_llm_generated=recommendation.is_llm_generated,
        )


class AnalysisResponse(BaseModel):
    resume_id: str
    job_description_id: str
    scorecard: ScoreCardSchema
    recommendations: List[RecommendationSchema]
    raw_text: Optional[str] = None

    @classmethod
    def from_domain(
        cls, resume_id: str, job_description_id: str, result: AnalysisResult
    ) -> "AnalysisResponse":
        return cls(
            resume_id=resume_id,
            job_description_id=job_description_id,
            scorecard=ScoreCardSchema.from_domain(result.scorecard),
            recommendations=[
                RecommendationSchema.from_domain(r) for r in result.recommendations
            ],
            raw_text=result.resume.raw_text,
        )


class TaskEnqueuedResponse(BaseModel):
    task_id: str
    status: str = "queued"


class TaskStatusResponse(BaseModel):
    task_id: str
    status: str  # PENDING | STARTED | SUCCESS | FAILURE
    result: Optional[AnalysisResponse] = None
    error: Optional[str] = None
