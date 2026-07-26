from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from app.application.dto import AnalysisResult
from app.application.ports import AnalysisRecord, IAnalysisRepository
from app.infrastructure.persistence.mappers import (
    recommendations_from_list,
    recommendations_to_list,
    scorecard_from_dict,
    scorecard_to_dict,
)
from app.infrastructure.persistence.models import AnalysisModel


class SQLAlchemyAnalysisRepository(IAnalysisRepository):
    """
    Stores only the scorecard + recommendations from an AnalysisResult,
    referencing resume/job_description by id (foreign keys) rather than
    re-embedding their full content -- those are already persisted
    separately by their own repositories. See AnalysisRecord's
    docstring in app/application/ports.py for why full AnalysisResult
    reconstruction is deliberately not this repository's job.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def save(
        self,
        analysis_result: AnalysisResult,
        *,
        resume_id: str,
        job_description_id: str,
        user_id: Optional[str] = None,
    ) -> AnalysisRecord:
        model = AnalysisModel(
            user_id=user_id,
            resume_id=resume_id,
            job_description_id=job_description_id,
            overall_score=analysis_result.scorecard.overall_score,
            scorecard_json=scorecard_to_dict(analysis_result.scorecard),
            recommendations_json=recommendations_to_list(
                analysis_result.recommendations
            ),
        )
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return self._to_record(model)

    def get_by_id(self, analysis_id: str) -> Optional[AnalysisRecord]:
        model = self._session.get(AnalysisModel, analysis_id)
        return self._to_record(model) if model else None

    def list_by_user(self, user_id: str) -> List[AnalysisRecord]:
        models = (
            self._session.query(AnalysisModel)
            .filter_by(user_id=user_id)
            .order_by(AnalysisModel.created_at.desc())
            .all()
        )
        return [self._to_record(m) for m in models]

    @staticmethod
    def _to_record(model: AnalysisModel) -> AnalysisRecord:
        return AnalysisRecord(
            id=str(model.id),
            resume_id=str(model.resume_id),
            job_description_id=str(model.job_description_id),
            user_id=str(model.user_id) if model.user_id else None,
            scorecard=scorecard_from_dict(model.scorecard_json),
            recommendations=recommendations_from_list(model.recommendations_json),
            created_at=model.created_at,
        )
