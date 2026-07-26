from __future__ import annotations

from typing import List

import pytest
from fastapi.testclient import TestClient

from app.api.dependencies import get_db
from app.api.main import create_app
from app.application.container import build_container
from app.domain.ports.embedder import IEmbedder
from app.domain.ports.llm_provider import ILLMProvider
from app.infrastructure.persistence.database import create_session_factory

_TEST_DATABASE_URL = (
    "postgresql+psycopg2://resume_scanner:resume_scanner_dev@localhost:5432/resume_scanner_test"
)


class FakeEmbedder(IEmbedder):
    def embed(self, texts: List[str]) -> List[List[float]]:
        return [[0.0] for _ in texts]

    def similarity(self, vector_a, vector_b) -> float:
        return 0.0


class FakeLLMProvider(ILLMProvider):
    def explain_evidence(self, evidence, *, context=None, max_tokens=300) -> str:
        return "Fake explanation."

    def suggest_improvement(self, failing_evidence, *, resume_context=None, max_tokens=200) -> str:
        return "Fake recommendation."


@pytest.fixture(scope="session")
def test_session_factory():
    return create_session_factory(_TEST_DATABASE_URL)


@pytest.fixture
def api_client(test_session_factory):
    """
    A TestClient wired to: real test PostgreSQL (via get_db override),
    a fake embedder + fake LLM (same sandbox network constraint as
    Phases 2/3), and everything else real -- real parsers, real
    scoring engine, real password hashing, real JWT signing.
    """
    container = build_container(
        embedder=FakeEmbedder(), llm_provider=FakeLLMProvider()
    )
    app = create_app(container=container)

    def _override_get_db():
        session = test_session_factory()
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = _override_get_db

    with TestClient(app) as client:
        yield client

    # Cleanup: repositories commit internally (see Phase 5), so clean
    # up explicitly after each test rather than relying on rollback.
    session = test_session_factory()
    from app.infrastructure.persistence.models import (
        AnalysisModel,
        JobDescriptionModel,
        ResumeModel,
        UserModel,
    )

    session.query(AnalysisModel).delete()
    session.query(ResumeModel).delete()
    session.query(JobDescriptionModel).delete()
    session.query(UserModel).delete()
    session.commit()
    session.close()


@pytest.fixture
def registered_user_token(api_client) -> dict:
    """Registers a user and returns {'headers': {...}, 'email':..., 'user_id':...}."""
    email = "test-user@example.com"
    password = "supersecret123"

    register_response = api_client.post(
        "/api/v1/auth/register",
        json={"email": email, "password": password, "full_name": "Test User"},
    )
    assert register_response.status_code == 201, register_response.text
    user_id = register_response.json()["id"]

    login_response = api_client.post(
        "/api/v1/auth/login",
        data={"username": email, "password": password},
    )
    assert login_response.status_code == 200, login_response.text
    token = login_response.json()["access_token"]

    return {
        "headers": {"Authorization": f"Bearer {token}"},
        "email": email,
        "user_id": user_id,
    }
