from __future__ import annotations

from typing import List, Optional

from sqlalchemy.orm import Session

from app.domain.entities.resume import Resume
from app.domain.ports.repository import IResumeRepository, ResumeRecord
from app.infrastructure.persistence.mappers import resume_from_dict, resume_to_dict
from app.infrastructure.persistence.models import ResumeModel


class SQLAlchemyResumeRepository(IResumeRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(
        self, resume: Resume, *, filename: str, user_id: Optional[str] = None
    ) -> ResumeRecord:
        model = ResumeModel(
            user_id=user_id,
            filename=filename,
            raw_text=resume.raw_text,
            parsed_json=resume_to_dict(resume),
        )
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return self._to_record(model)

    def get_by_id(self, resume_id: str) -> Optional[ResumeRecord]:
        model = self._session.get(ResumeModel, resume_id)
        return self._to_record(model) if model else None

    def list_by_user(self, user_id: str) -> List[ResumeRecord]:
        models = (
            self._session.query(ResumeModel)
            .filter_by(user_id=user_id)
            .order_by(ResumeModel.created_at.desc())
            .all()
        )
        return [self._to_record(m) for m in models]

    def delete(self, resume_id: str) -> bool:
        model = self._session.get(ResumeModel, resume_id)
        if model is None:
            return False
        self._session.delete(model)
        self._session.commit()
        return True

    @staticmethod
    def _to_record(model: ResumeModel) -> ResumeRecord:
        return ResumeRecord(
            id=str(model.id),
            resume=resume_from_dict(model.parsed_json),
            filename=model.filename,
            user_id=str(model.user_id) if model.user_id else None,
            created_at=model.created_at,
        )
