"""
Typed response schemas for Resume, built explicitly from the domain
entity (via `from_domain`) rather than returning the raw dict shape
mappers.py uses for JSONB storage. Two different serialization
concerns, kept separate deliberately: the JSONB shape is a storage
format that can evolve independently of the public API contract.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import List, Optional

from pydantic import BaseModel

from app.domain.entities.resume import Resume


class ContactInfoSchema(BaseModel):
    full_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    location: Optional[str]
    linkedin_url: Optional[str]


class SkillSchema(BaseModel):
    name: str
    normalized_name: str
    category: Optional[str]


class DateRangeSchema(BaseModel):
    start: date
    end: Optional[date]
    is_current: bool


class ExperienceEntrySchema(BaseModel):
    title: str
    company: str
    date_range: DateRangeSchema
    bullets: List[str]


class EducationEntrySchema(BaseModel):
    degree: str
    field_of_study: str
    institution: str
    graduation_date: Optional[date]
    gpa: Optional[float]


class ProjectEntrySchema(BaseModel):
    name: str
    description: str
    technologies: List[str]
    outcomes: List[str]


class CertificationEntrySchema(BaseModel):
    name: str
    issuer: Optional[str]
    date_earned: Optional[date]


class FormattingFlagsSchema(BaseModel):
    uses_tables: bool
    uses_text_boxes: bool
    non_standard_fonts: bool
    has_images_with_text: bool
    page_count: int


class ResumeResponse(BaseModel):
    id: str
    filename: str
    contact_info: ContactInfoSchema
    skills: List[SkillSchema]
    experience: List[ExperienceEntrySchema]
    education: List[EducationEntrySchema]
    projects: List[ProjectEntrySchema]
    certifications: List[CertificationEntrySchema]
    sections_detected: List[str]
    formatting_flags: FormattingFlagsSchema
    total_experience_years: float
    created_at: datetime

    @classmethod
    def from_domain(
        cls, resume_id: str, resume: Resume, filename: str, created_at: datetime
    ) -> "ResumeResponse":
        return cls(
            id=resume_id,
            filename=filename,
            contact_info=ContactInfoSchema(**vars(resume.contact_info)),
            skills=[
                SkillSchema(name=s.name, normalized_name=s.normalized_name, category=s.category)
                for s in resume.skills
            ],
            experience=[
                ExperienceEntrySchema(
                    title=e.title,
                    company=e.company,
                    date_range=DateRangeSchema(
                        start=e.date_range.start,
                        end=e.date_range.end,
                        is_current=e.date_range.is_current,
                    ),
                    bullets=e.bullets,
                )
                for e in resume.experience
            ],
            education=[
                EducationEntrySchema(
                    degree=ed.degree,
                    field_of_study=ed.field_of_study,
                    institution=ed.institution,
                    graduation_date=ed.graduation_date,
                    gpa=ed.gpa,
                )
                for ed in resume.education
            ],
            projects=[
                ProjectEntrySchema(
                    name=p.name,
                    description=p.description,
                    technologies=p.technologies,
                    outcomes=p.outcomes,
                )
                for p in resume.projects
            ],
            certifications=[
                CertificationEntrySchema(
                    name=c.name, issuer=c.issuer, date_earned=c.date_earned
                )
                for c in resume.certifications
            ],
            sections_detected=resume.sections_detected,
            formatting_flags=FormattingFlagsSchema(
                uses_tables=resume.formatting_flags.uses_tables,
                uses_text_boxes=resume.formatting_flags.uses_text_boxes,
                non_standard_fonts=resume.formatting_flags.non_standard_fonts,
                has_images_with_text=resume.formatting_flags.has_images_with_text,
                page_count=resume.formatting_flags.page_count,
            ),
            total_experience_years=resume.total_experience_years,
            created_at=created_at,
        )
