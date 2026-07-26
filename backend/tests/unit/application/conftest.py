from __future__ import annotations

from datetime import date

import pytest

from app.domain.entities.job_description import JobDescription
from app.domain.entities.resume import (
    ContactInfo,
    DateRange,
    ExperienceEntry,
    FormattingFlags,
    Resume,
    Skill,
)
from app.domain.ports.embedder import IEmbedder
from app.domain.ports.llm_provider import ILLMProvider
from app.domain.ports.parser import IJobDescriptionParser, IResumeParser


@pytest.fixture
def fixed_resume() -> Resume:
    return Resume(
        raw_text="Jane Smith resume text",
        contact_info=ContactInfo(
            full_name="Jane Smith", email="jane@example.com", phone="555-1234"
        ),
        skills=[Skill(name="Python", normalized_name="python")],
        experience=[
            ExperienceEntry(
                title="Backend Engineer",
                company="Acme Corp",
                date_range=DateRange(start=date(2021, 1, 1), end=date(2023, 6, 1)),
                bullets=["Built a scalable REST API"],
            )
        ],
        sections_detected=["experience", "skills"],
        formatting_flags=FormattingFlags(),
    )


@pytest.fixture
def fixed_job_description() -> JobDescription:
    return JobDescription(
        raw_text="Backend Engineer job",
        title="Backend Engineer",
        required_skills=["Python", "Kubernetes"],  # Kubernetes will fail -> evidence
        min_years_experience=10.0,  # will fail -> high-weight evidence
    )


class FakeEmbedder(IEmbedder):
    """Deterministic, zero-overlap fake: nothing semantically matches anything."""

    def embed(self, texts):
        return [[0.0] for _ in texts]

    def similarity(self, vector_a, vector_b) -> float:
        return 0.0


class FakeLLMProvider(ILLMProvider):
    def __init__(self, response: str = "LLM-generated recommendation.") -> None:
        self._response = response
        self.explain_calls = 0
        self.suggest_calls = 0

    def explain_evidence(self, evidence, *, context=None, max_tokens=300) -> str:
        self.explain_calls += 1
        return self._response

    def suggest_improvement(
        self, failing_evidence, *, resume_context=None, max_tokens=200
    ) -> str:
        self.suggest_calls += 1
        return self._response


class FailingLLMProvider(ILLMProvider):
    """Simulates any real-world LLM failure (network error, ungrounded, etc)."""

    def explain_evidence(self, evidence, *, context=None, max_tokens=300) -> str:
        raise RuntimeError("simulated LLM failure")

    def suggest_improvement(
        self, failing_evidence, *, resume_context=None, max_tokens=200
    ) -> str:
        raise RuntimeError("simulated LLM failure")


@pytest.fixture
def fake_embedder() -> FakeEmbedder:
    return FakeEmbedder()


@pytest.fixture
def fake_llm_provider() -> FakeLLMProvider:
    return FakeLLMProvider()


@pytest.fixture
def failing_llm_provider() -> FailingLLMProvider:
    return FailingLLMProvider()


class FakeResumeParser(IResumeParser):
    def __init__(self, resume: Resume) -> None:
        self._resume = resume
        self.parse_calls: list[tuple[bytes, str]] = []

    def parse(self, file_bytes: bytes, filename: str) -> Resume:
        self.parse_calls.append((file_bytes, filename))
        return self._resume


class FakeJobDescriptionParser(IJobDescriptionParser):
    def __init__(self, job_description: JobDescription) -> None:
        self._job_description = job_description
        self.parse_calls: list[str] = []

    def parse(self, text: str) -> JobDescription:
        self.parse_calls.append(text)
        return self._job_description


@pytest.fixture
def fake_resume_parser(fixed_resume) -> FakeResumeParser:
    return FakeResumeParser(fixed_resume)


@pytest.fixture
def fake_jd_parser(fixed_job_description) -> FakeJobDescriptionParser:
    return FakeJobDescriptionParser(fixed_job_description)
