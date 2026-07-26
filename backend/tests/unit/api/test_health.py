from __future__ import annotations


def test_liveness_has_zero_dependencies_and_always_succeeds(api_client):
    response = api_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_readiness_reports_healthy_when_db_and_redis_are_up(api_client):
    response = api_client.get("/health/ready")
    assert response.status_code == 200
    body = response.json()
    assert body["ready"] is True
    assert body["checks"]["database"] is True
    assert body["checks"]["redis"] is True


def test_readiness_check_function_detects_real_db_failure():
    """
    Unit-level test of the readiness logic itself (not the HTTP layer)
    -- passes a session pointed at a nonexistent database to prove
    check_readiness() actually attempts a real query rather than
    always returning True.
    """
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker

    from app.api.health import check_readiness

    bad_engine = create_engine(
        "postgresql+psycopg2://nonexistent:nonexistent@localhost:5432/nonexistent",
        pool_pre_ping=False,
    )
    BadSession = sessionmaker(bind=bad_engine)
    session = BadSession()

    try:
        result = check_readiness(session)
        assert result.checks["database"] is False
        assert result.ready is False
    finally:
        session.close()
