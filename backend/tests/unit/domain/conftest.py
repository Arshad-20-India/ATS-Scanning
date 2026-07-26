from __future__ import annotations

from datetime import date
from typing import List

import pytest

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
from app.domain.ports.embedder import IEmbedder


@pytest.fixture
def sample_resume() -> Resume:
    return Resume(
        raw_text="John Doe resume text...",
        contact_info=ContactInfo(
            full_name="John Doe",
            email="john@example.com",
            phone="555-1234",
        ),
        skills=[
            Skill(name="Python", normalized_name="python"),
            Skill(name="JS", normalized_name="js"),
            Skill(name="Docker", normalized_name="docker"),
        ],
        experience=[
            ExperienceEntry(
                title="Backend Engineer",
                company="Acme Corp",
                date_range=DateRange(start=date(2021, 1, 1), end=date(2023, 6, 1)),
                bullets=[
                    "Built a scalable REST API serving 10k requests/sec using FastAPI",
                    "Reduced database query latency by 40% through indexing",
                ],
            ),
            ExperienceEntry(
                title="Software Engineer",
                company="Beta Inc",
                date_range=DateRange(start=date(2023, 8, 1), end=None),
                bullets=["Migrated monolith to microservices architecture"],
            ),
        ],
        education=[
            EducationEntry(
                degree="Bachelor of Science",
                field_of_study="Computer Science",
                institution="State University",
                graduation_date=date(2020, 5, 1),
            )
        ],
        projects=[
            ProjectEntry(
                name="Open Source CLI Tool",
                description="A CLI tool for automating deployments",
                technologies=["python", "docker"],
                outcomes=["Adopted by 500+ users", "Reduced deploy time by 30%"],
            )
        ],
        certifications=[CertificationEntry(name="AWS Certified Developer")],
        sections_detected=["experience", "education", "skills", "projects"],
        formatting_flags=FormattingFlags(
            uses_tables=False,
            uses_text_boxes=False,
            non_standard_fonts=False,
            has_images_with_text=False,
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
            weak_verb_count=1,
            avg_bullet_length_words=14.0,
            quantified_bullet_ratio=0.6,
        ),
    )


@pytest.fixture
def sample_job_description() -> JobDescription:
    return JobDescription(
        raw_text="We are looking for a backend engineer...",
        title="Backend Engineer",
        required_skills=["Python", "JavaScript"],
        preferred_skills=["Kubernetes"],
        min_years_experience=2.0,
        required_education="Bachelor",
        required_certifications=["AWS Certified Developer"],
        requirements=[
            JobRequirement(
                text="Experience building and scaling REST APIs",
                requirement_type="experience",
                weight=1.0,
            )
        ],
    )


class FakeEmbedder(IEmbedder):
    """
    Deterministic fake used across tests: assigns similarity based on
    shared word overlap so tests are predictable without loading a
    real sentence-transformers model.
    """

    def embed(self, texts: List[str]) -> List[List[float]]:
        # Represent each text as a fixed-size bag-of-words vector over
        # a small fake vocabulary for deterministic overlap-based scoring.
        vocab = [
            "api", "rest", "scaling", "scalable", "database", "python",
            "cli", "deploy", "microservices",
        ]
        vectors = []
        for text in texts:
            lowered = text.lower()
            vectors.append([1.0 if word in lowered else 0.0 for word in vocab])
        return vectors

    def similarity(self, vector_a: List[float], vector_b: List[float]) -> float:
        if not any(vector_a) or not any(vector_b):
            return 0.0
        overlap = sum(1 for a, b in zip(vector_a, vector_b) if a == 1.0 and b == 1.0)
        total = sum(1 for a, b in zip(vector_a, vector_b) if a == 1.0 or b == 1.0)
        return overlap / total if total else 0.0


@pytest.fixture
def fake_embedder() -> FakeEmbedder:
    return FakeEmbedder()
