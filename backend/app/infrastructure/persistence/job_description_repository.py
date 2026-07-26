from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from app.domain.entities.job_description import JobDescription
from app.domain.ports.repository import IJobDescriptionRepository, JobDescriptionRecord
from app.infrastructure.persistence.mappers import (
    job_description_from_dict,
    job_description_to_dict,
)
from app.infrastructure.persistence.models import JobDescriptionModel


class SQLAlchemyJobDescriptionRepository(IJobDescriptionRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(
        self, job_description: JobDescription, *, user_id: Optional[str] = None
    ) -> JobDescriptionRecord:
        model = JobDescriptionModel(
            user_id=user_id,
            title=job_description.title,
            raw_text=job_description.raw_text,
            parsed_json=job_description_to_dict(job_description),
        )
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return self._to_record(model)

    def get_by_id(self, job_description_id: str) -> Optional[JobDescriptionRecord]:
        model = self._session.get(JobDescriptionModel, job_description_id)
        return self._to_record(model) if model else None

    def list_by_user(self, user_id: str) -> List[JobDescriptionRecord]:
        models = (
            self._session.query(JobDescriptionModel)
            .filter_by(user_id=user_id)
            .order_by(JobDescriptionModel.created_at.desc())
            .all()
        )
        return [self._to_record(m) for m in models]

    @staticmethod
    def _to_record(model: JobDescriptionModel) -> JobDescriptionRecord:
        return JobDescriptionRecord(
            id=str(model.id),
            job_description=job_description_from_dict(model.parsed_json),
            user_id=str(model.user_id) if model.user_id else None,
            created_at=model.created_at,
        )
