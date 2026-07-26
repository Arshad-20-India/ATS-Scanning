from __future__ import annotations

import base64
import io
from typing import List

import docx
import pytest

from app.application.container import build_container
from app.domain.ports.embedder import IEmbedder
from app.domain.ports.llm_provider import ILLMProvider
from app.infrastructure.persistence.database import create_session_factory
from app.infrastructure.tasks.analysis_tasks import run_analysis

_TEST_DATABASE_URL = (
    "postgresql+psycopg2://resume_scanner:resume_scanner_dev@localhost:5432/resume_scanner_test"
)


class _FakeEmbedder(IEmbedder):
    def embed(self, texts: List[str]) -> List[List[float]]:
        return [[0.0] for _ in texts]

    def similarity(self, vector_a, vector_b) -> float:
        return 0.0


class _FakeLLMProvider(ILLMProvider):
    def explain_evidence(self, evidence, *, context=None, max_tokens=300) -> str:
        return "explanation"

    def suggest_improvement(self, failing_evidence, *, resume_context=None, max_tokens=200) -> str:
        return "suggestion"


@pytest.fixture
def sample_resume_bytes_b64() -> str:
    document = docx.Document()
    for line in ["Jane Smith", "jane@example.com", "", "Experience", "Engineer, Acme",
                 "Jan 2021 - Jun 2023", "- Did things", "", "Skills", "Python"]:
        document.add_paragraph(line)
    buf = io.BytesIO()
    document.save(buf)
    return base64.b64encode(buf.getvalue()).decode("ascii")


@pytest.fixture(autouse=True)
def cleanup_test_db():
    yield
    session_factory = create_session_factory(_TEST_DATABASE_URL)
    session = session_factory()
    from app.infrastructure.persistence.models import AnalysisModel, JobDescriptionModel, ResumeModel

    session.query(AnalysisModel).delete()
    session.query(ResumeModel).delete()
    session.query(JobDescriptionModel).delete()
    session.commit()
    session.close()


def test_run_analysis_with_injected_container_no_celery_needed(sample_resume_bytes_b64, monkeypatch):
    # Point the task's persistence at the test database, not dev.
    import app.infrastructure.tasks.analysis_tasks as tasks_module

    monkeypatch.setattr(
        tasks_module, "SessionLocal", create_session_factory(_TEST_DATABASE_URL)
    )

    container = build_container(embedder=_FakeEmbedder(), llm_provider=_FakeLLMProvider())

    result_dict = run_analysis(
        sample_resume_bytes_b64,
        "resume.docx",
        "Backend Engineer\n\nRequired\n- Python",
        container=container,
    )

    assert result_dict["scorecard"]["overall_score"] >= 0.0
    assert "resume_id" in result_dict
    assert "job_description_id" in result_dict


def test_run_analysis_persists_to_database(sample_resume_bytes_b64, monkeypatch):
    import app.infrastructure.tasks.analysis_tasks as tasks_module

    test_session_factory = create_session_factory(_TEST_DATABASE_URL)
    monkeypatch.setattr(tasks_module, "SessionLocal", test_session_factory)

    container = build_container(embedder=_FakeEmbedder(), llm_provider=_FakeLLMProvider())
    result_dict = run_analysis(
        sample_resume_bytes_b64, "resume.docx", "Backend Engineer\n\nRequired\n- Python",
        container=container,
    )

    from app.infrastructure.persistence.resume_repository import SQLAlchemyResumeRepository

    session = test_session_factory()
    record = SQLAlchemyResumeRepository(session).get_by_id(result_dict["resume_id"])
    session.close()

    assert record is not None
    assert record.resume.contact_info.full_name == "Jane Smith"
