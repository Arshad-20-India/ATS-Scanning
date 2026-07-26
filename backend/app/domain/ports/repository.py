"""
Repository ports for the two domain entities that get persisted:
Resume and JobDescription.

Design note on the *Record wrapper types: Resume and JobDescription
(Phase 1) are deliberately pure computation objects with no `id` or
`created_at` -- they represent parsed content, not storage identity.
Persistence identity is a separate concern, so it's modeled here as a
thin wrapper (`ResumeRecord`, `JobDescriptionRecord`) rather than by
retrofitting id/timestamp fields onto the frozen Phase 1 entities,
which would leak a storage concern into the domain's core data model.

Note on AnalysisResult: its repository port (`IAnalysisRepository`)
is deliberately NOT defined here. AnalysisResult is an
application-layer concept (see app/application/dto.py), so its
repository interface lives in app/application/ports.py -- domain must
never depend on application. This module only depends on entities.py,
consistent with the dependency direction enforced throughout the
project.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from app.domain.entities.job_description import JobDescription
from app.domain.entities.resume import Resume


@dataclass(frozen=True)
class ResumeRecord:
    id: str
    resume: Resume
    filename: str
    user_id: Optional[str]
    created_at: datetime


@dataclass(frozen=True)
class JobDescriptionRecord:
    id: str
    job_description: JobDescription
    user_id: Optional[str]
    created_at: datetime


class IResumeRepository(ABC):
    @abstractmethod
    def save(
        self, resume: Resume, *, filename: str, user_id: Optional[str] = None
    ) -> ResumeRecord:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, resume_id: str) -> Optional[ResumeRecord]:
        raise NotImplementedError

    @abstractmethod
    def list_by_user(self, user_id: str) -> List[ResumeRecord]:
        raise NotImplementedError

    @abstractmethod
    def delete(self, resume_id: str) -> bool:
        raise NotImplementedError


class IJobDescriptionRepository(ABC):
    @abstractmethod
    def save(
        self, job_description: JobDescription, *, user_id: Optional[str] = None
    ) -> JobDescriptionRecord:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, job_description_id: str) -> Optional[JobDescriptionRecord]:
        raise NotImplementedError

    @abstractmethod
    def list_by_user(self, user_id: str) -> List[JobDescriptionRecord]:
        raise NotImplementedError
