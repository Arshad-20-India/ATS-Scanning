"""
User persistence for authentication.

Deliberately NOT behind a domain port (no IUserRepository in
app/domain/ports): User/authentication is an infrastructure/API
concern (who is allowed to call the system), not part of the
resume-scoring domain model Phases 1-5 were built around. Introducing
a domain port for it would suggest scoring logic might someday depend
on user identity, which it deliberately never should (see
ScoringPolicy/aggregate_evidence -- scores are pure functions of
Resume + JobDescription, full stop). This repository is used directly
by the API layer's auth router.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from sqlalchemy.orm import Session

from app.infrastructure.persistence.models import UserModel


@dataclass(frozen=True)
class UserRecord:
    id: str
    email: str
    hashed_password: str
    full_name: Optional[str]
    created_at: datetime


class UserRepository:
    def __init__(self, session: Session) -> None:
        self._session = session

    def create(
        self, email: str, hashed_password: str, full_name: Optional[str] = None
    ) -> UserRecord:
        model = UserModel(
            email=email, hashed_password=hashed_password, full_name=full_name
        )
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return self._to_record(model)

    def get_by_email(self, email: str) -> Optional[UserRecord]:
        model = self._session.query(UserModel).filter_by(email=email).first()
        return self._to_record(model) if model else None

    def get_by_id(self, user_id: str) -> Optional[UserRecord]:
        model = self._session.get(UserModel, user_id)
        return self._to_record(model) if model else None

    @staticmethod
    def _to_record(model: UserModel) -> UserRecord:
        return UserRecord(
            id=str(model.id),
            email=model.email,
            hashed_password=model.hashed_password,
            full_name=model.full_name,
            created_at=model.created_at,
        )
