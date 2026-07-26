"""
Async analysis task.

Design note: the actual logic lives in `run_analysis()`, a plain
function that accepts an optional `container` parameter. The Celery
task (`run_analysis_task`) is a thin wrapper around it. This split
means:

  1. Tests call `run_analysis()` directly with an injected fake
     container -- no Celery worker, no real broker, no network needed.
  2. A separate integration test proves the Celery wiring itself
     works, using `task_always_eager` (see
     tests/unit/infrastructure/tasks/), without needing a live worker
     process in the test environment.

The container is memoized per worker process (module-level, built
lazily on first task execution) since it may hold expensive model
state -- rebuilding it per task would defeat the point of a persistent
worker process.
"""

from __future__ import annotations

import base64
import time
from typing import Optional

from app.api.metrics import record_analysis_metrics
from app.api.schemas.analysis_schemas import AnalysisResponse
from app.application.container import ApplicationContainer, build_container
from app.infrastructure.persistence.analysis_repository import (
    SQLAlchemyAnalysisRepository,
)
from app.infrastructure.persistence.database import SessionLocal
from app.infrastructure.persistence.job_description_repository import (
    SQLAlchemyJobDescriptionRepository,
)
from app.infrastructure.persistence.resume_repository import SQLAlchemyResumeRepository
from app.infrastructure.tasks.celery_app import celery_app

_worker_container: Optional[ApplicationContainer] = None


def _get_worker_container() -> ApplicationContainer:
    global _worker_container
    if _worker_container is None:
        _worker_container = build_container()
    return _worker_container


def run_analysis(
    resume_bytes_b64: str,
    filename: str,
    job_description_text: str,
    user_id: Optional[str] = None,
    container: Optional[ApplicationContainer] = None,
) -> dict:
    """
    The real logic. `container` is injectable so tests never touch a
    real embedder/LLM/Celery broker.
    """
    resolved_container = container or _get_worker_container()
    file_bytes = base64.b64decode(resume_bytes_b64)

    start = time.perf_counter()
    result = resolved_container.analyze_resume_use_case.execute(
        file_bytes, filename, job_description_text
    )
    duration = time.perf_counter() - start
    record_analysis_metrics(result, mode="async", duration_seconds=duration)

    session = SessionLocal()
    try:
        resume_record = SQLAlchemyResumeRepository(session).save(
            result.resume, filename=filename, user_id=user_id
        )
        jd_record = SQLAlchemyJobDescriptionRepository(session).save(
            result.job_description, user_id=user_id
        )
        SQLAlchemyAnalysisRepository(session).save(
            result,
            resume_id=resume_record.id,
            job_description_id=jd_record.id,
            user_id=user_id,
        )
    finally:
        session.close()

    response = AnalysisResponse.from_domain(resume_record.id, jd_record.id, result)
    return response.model_dump(mode="json")


@celery_app.task(name="analysis.run_analysis", bind=False)
def run_analysis_task(
    resume_bytes_b64: str,
    filename: str,
    job_description_text: str,
    user_id: Optional[str] = None,
) -> dict:
    return run_analysis(resume_bytes_b64, filename, job_description_text, user_id)
