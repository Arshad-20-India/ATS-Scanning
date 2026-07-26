from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.domain.entities.job_description import JobDescription


class JobDescriptionCreateRequest(BaseModel):
    text: str = Field(min_length=20, description="Raw job description text")


class JobDescriptionResponse(BaseModel):
    id: str
    title: str
    required_skills: List[str]
    preferred_skills: List[str]
    min_years_experience: Optional[float]
    required_education: Optional[str]
    required_certifications: List[str]
    created_at: datetime

    @classmethod
    def from_domain(
        cls, jd_id: str, jd: JobDescription, created_at: datetime
    ) -> "JobDescriptionResponse":
        return cls(
            id=jd_id,
            title=jd.title,
            required_skills=jd.required_skills,
            preferred_skills=jd.preferred_skills,
            min_years_experience=jd.min_years_experience,
            required_education=jd.required_education,
            required_certifications=jd.required_certifications,
            created_at=created_at,
        )
