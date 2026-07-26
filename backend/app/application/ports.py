"""
Application-layer ports.

IAnalysisRepository lives here rather than in app/domain/ports because
its payload is built from AnalysisResult (see dto.py), an
application-layer concept -- domain must never depend on application,
so a port operating on an application-derived type cannot live in
domain. This mirrors exactly how app/domain/ports/repository.py hosts
IResumeRepository/IJobDescriptionRepository, which operate on domain
entities.

Design note on AnalysisRecord: it deliberately stores `scorecard` and
`recommendations` directly rather than wrapping a full AnalysisResult.
AnalysisResult.resume/.job_description are non-optional Resume/
JobDescription (Phase 4) -- populating them from a bare analysis
lookup would mean either faking those fields or performing extra
repository calls the caller didn't ask for. Reconstructing the
complete AnalysisResult when it's actually needed is a matter of
combining an AnalysisRecord with a IResumeRepository/
IJobDescriptionRepository lookup by id -- an application-layer
concern, not this port's job.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from app.application.dto import AnalysisResult, Recommendation
from app.domain.entities.score import ScoreCard


@dataclass(frozen=True)
class AnalysisRecord:
    id: str
    resume_id: str
    job_description_id: str
    user_id: Optional[str]
    scorecard: ScoreCard
    recommendations: List[Recommendation]
    created_at: datetime


class IAnalysisRepository(ABC):
    @abstractmethod
    def save(
        self,
        analysis_result: AnalysisResult,
        *,
        resume_id: str,
        job_description_id: str,
        user_id: Optional[str] = None,
    ) -> AnalysisRecord:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, analysis_id: str) -> Optional[AnalysisRecord]:
        raise NotImplementedError

    @abstractmethod
    def list_by_user(self, user_id: str) -> List[AnalysisRecord]:
        raise NotImplementedError
