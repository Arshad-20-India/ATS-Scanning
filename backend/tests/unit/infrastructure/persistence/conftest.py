"""
Persistence test fixtures.

These tests run against a REAL PostgreSQL database (resume_scanner_test)
and a REAL Redis instance, not mocks -- the whole point of this layer
is correct SQL/ORM behavior and correct JSON round-tripping, which a
mock can't verify. Each test gets a fresh transaction that is rolled
back at teardown, so tests never leave data behind or interfere with
each other, without needing to recreate the schema per test.
"""

from __future__ import annotations

from datetime import date

import pytest
import redis
from sqlalchemy.orm import Session

from app.domain.entities.job_description import JobDescription, JobRequirement
from app.domain.entities.resume import (
    CertificationEntry,
    ContactInfo,
    DateRange,
    EducationEntry,
    ExperienceEntry,
    FormattingFlags,
    GrammarFinding,
    ProjectEntry,
    Resume,
    Skill,
    WritingMetrics,
)
from app.infrastructure.persistence.database import create_session_factory

_TEST_DATABASE_URL = (
    "postgresql+psycopg2://resume_scanner:resume_scanner_dev@localhost:5432/resume_scanner_test"
)
_TEST_REDIS_URL = "redis://localhost:6379/1"  # separate DB index from prod default (0)


@pytest.fixture(scope="session")
def test_session_factory():
    return create_session_factory(_TEST_DATABASE_URL)


@pytest.fixture
def db_session(test_session_factory) -> Session:
    """
    Repositories under test call session.commit() internally (real
    production behavior), which would break a savepoint/rollback-based
    isolation strategy -- an inner commit releases the outer
    transaction too. So isolation here is honest explicit cleanup
    after each test instead: delete all rows in FK-safe order.
    """
    from app.infrastructure.persistence.models import (
        AnalysisModel,
        JobDescriptionModel,
        ResumeModel,
        UserModel,
    )

    session = test_session_factory()
    try:
        yield session
    finally:
        session.rollback()
        session.query(AnalysisModel).delete()
        session.query(ResumeModel).delete()
        session.query(JobDescriptionModel).delete()
        session.query(UserModel).delete()
        session.commit()
        session.close()


@pytest.fixture
def redis_client():
    client = redis.from_url(_TEST_REDIS_URL, decode_responses=True)
    client.flushdb()
    yield client
    client.flushdb()
    client.close()


@pytest.fixture
def make_test_user(db_session):
    """
    Creates a real User row and returns its id -- needed because
    resumes.user_id / job_descriptions.user_id / analyses.user_id all
    have a real foreign-key constraint to users.id (correctly so: it's
    what caught a bug in an earlier draft of these tests that used
    made-up UUIDs and got rejected by the database, exactly as it
    should).
    """
    from app.infrastructure.persistence.models import UserModel

    def _make(email: str = "test@example.com") -> str:
        user = UserModel(email=email, hashed_password="not-a-real-hash")
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        return str(user.id)

    return _make


@pytest.fixture
def full_resume() -> Resume:
    """A Resume exercising every nested field, to stress-test the mappers."""
    return Resume(
        raw_text="Full resume text with everything in it.",
        contact_info=ContactInfo(
            full_name="Jane Smith",
            email="jane@example.com",
            phone="555-1234",
            location="Austin, TX",
            linkedin_url="linkedin.com/in/janesmith",
        ),
        skills=[
            Skill(name="Python", normalized_name="python", category="language"),
            Skill(name="Docker", normalized_name="docker", source_section="Skills"),
        ],
        experience=[
            ExperienceEntry(
                title="Backend Engineer",
                company="Acme Corp",
                date_range=DateRange(start=date(2021, 1, 1), end=date(2023, 6, 1)),
                bullets=["Built a scalable REST API", "Reduced latency by 40%"],
                skills_mentioned=["Python", "FastAPI"],
            ),
            ExperienceEntry(
                title="Software Engineer",
                company="Beta Inc",
                date_range=DateRange(start=date(2023, 8, 1), end=None),
                bullets=["Migrated monolith to microservices"],
            ),
        ],
        education=[
            EducationEntry(
                degree="Bachelor of Science",
                field_of_study="Computer Science",
                institution="State University",
                graduation_date=date(2020, 5, 1),
                gpa=3.8,
            )
        ],
        projects=[
            ProjectEntry(
                name="CLI Tool",
                description="Automates deployments",
                technologies=["Python", "Docker"],
                outcomes=["Adopted by 500 users"],
            )
        ],
        certifications=[
            CertificationEntry(
                name="AWS Certified Developer",
                issuer="Amazon",
                date_earned=date(2022, 3, 1),
                expires=date(2025, 3, 1),
            )
        ],
        sections_detected=["experience", "education", "skills", "projects", "certifications"],
        formatting_flags=FormattingFlags(
            uses_tables=False,
            uses_text_boxes=False,
            uses_columns=True,
            non_standard_fonts=False,
            has_images_with_text=False,
            page_count=2,
        ),
        grammar_findings=[
            GrammarFinding(
                rule_id="PASSIVE_VOICE",
                message="Consider active voice",
                severity="warning",
                span="was built by the team",
            )
        ],
        writing_metrics=WritingMetrics(
            passive_voice_ratio=0.1,
            weak_verb_count=2,
            avg_bullet_length_words=12.5,
            quantified_bullet_ratio=0.6,
        ),
    )


@pytest.fixture
def full_job_description() -> JobDescription:
    return JobDescription(
        raw_text="Full JD text",
        title="Backend Engineer",
        required_skills=["Python", "Docker"],
        preferred_skills=["Kubernetes"],
        min_years_experience=3.0,
        required_education="Bachelor",
        required_certifications=["AWS Certified Developer"],
        requirements=[
            JobRequirement(
                text="Experience building REST APIs",
                requirement_type="experience",
                weight=1.0,
            )
        ],
    )
