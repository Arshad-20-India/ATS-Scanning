"""
Analysis endpoints.

Two modes are exposed deliberately:
  - POST /analyses/sync: runs AnalyzeResumeUseCase in-process and
    returns the full result immediately. Simple, but ties up a request
    worker for the duration of parsing + embedding + LLM calls.
  - POST /analyses/async: enqueues the same work as a Celery task and
    returns a task_id immediately; the client polls
    GET /analyses/tasks/{task_id}. This is the one to use for anything
    latency-sensitive at the HTTP layer, or under real load.

Both persist identically (same repositories, same schema) -- the only
difference is whether the work happens inline or on a worker.

Phase 9 additions: rate limiting (the expensive endpoints -- parsing +
embedding + optionally an LLM call -- are the ones worth protecting
from abuse), an explicit upload size cap (rejecting oversized files
before they're read into memory), and business metrics recorded via
record_analysis_metrics (see app/api/metrics.py for why that stays a
pure API-layer concern rather than leaking into the use case).
"""

import base64
import time
from typing import Optional

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_container, get_current_user_optional, get_db
from app.api.metrics import record_analysis_metrics
from app.api.rate_limit import limiter
from app.api.schemas.analysis_schemas import (
    AnalysisResponse,
    RecommendationSchema,
    ScoreCardSchema,
    TaskEnqueuedResponse,
    TaskStatusResponse,
)
from app.application.container import ApplicationContainer
from app.core.config import settings
from app.infrastructure.persistence.analysis_repository import (
    SQLAlchemyAnalysisRepository,
)
from app.infrastructure.persistence.job_description_repository import (
    SQLAlchemyJobDescriptionRepository,
)
from app.infrastructure.persistence.resume_repository import SQLAlchemyResumeRepository
from app.infrastructure.persistence.user_repository import UserRecord
from app.infrastructure.tasks.analysis_tasks import run_analysis_task
from app.infrastructure.tasks.celery_app import celery_app

router = APIRouter(prefix="/analyses", tags=["analyses"])


def _reject_if_oversized(file_bytes: bytes) -> None:
    if len(file_bytes) > settings.max_upload_size_bytes:
        raise HTTPException(
            status.HTTP_413_CONTENT_TOO_LARGE,
            f"File exceeds the {settings.max_upload_size_bytes // (1024 * 1024)}MB upload limit.",
        )


@router.post("/sync", response_model=AnalysisResponse)
@limiter.limit(settings.rate_limit_analysis)
async def analyze_sync(
    request: Request,
    resume_file: UploadFile = File(...),
    job_description_text: str = Form(...),
    container: ApplicationContainer = Depends(get_container),
    db: Session = Depends(get_db),
    current_user: Optional[UserRecord] = Depends(get_current_user_optional),
) -> AnalysisResponse:
    file_bytes = await resume_file.read()
    _reject_if_oversized(file_bytes)

    start = time.perf_counter()
    try:
        result = container.analyze_resume_use_case.execute(
            file_bytes, resume_file.filename, job_description_text
        )
    except Exception as err:
        err_msg = str(err)
        if "not appear to be a candidate resume" in err_msg or "insufficient text" in err_msg or "Unsupported file type" in err_msg:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err_msg)
        raise err
    duration = time.perf_counter() - start
    record_analysis_metrics(result, mode="sync", duration_seconds=duration)

    user_id = current_user.id if current_user else None
    resume_record = SQLAlchemyResumeRepository(db).save(
        result.resume, filename=resume_file.filename, user_id=user_id
    )
    jd_record = SQLAlchemyJobDescriptionRepository(db).save(
        result.job_description, user_id=user_id
    )
    SQLAlchemyAnalysisRepository(db).save(
        result, resume_id=resume_record.id, job_description_id=jd_record.id, user_id=user_id
    )

    return AnalysisResponse.from_domain(resume_record.id, jd_record.id, result)


@router.post("/async", response_model=TaskEnqueuedResponse, status_code=status.HTTP_202_ACCEPTED)
@limiter.limit(settings.rate_limit_analysis)
async def analyze_async(
    request: Request,
    resume_file: UploadFile = File(...),
    job_description_text: str = Form(...),
    current_user: Optional[UserRecord] = Depends(get_current_user_optional),
) -> TaskEnqueuedResponse:
    file_bytes = await resume_file.read()
    _reject_if_oversized(file_bytes)

    resume_bytes_b64 = base64.b64encode(file_bytes).decode("ascii")
    user_id = current_user.id if current_user else None

    task = run_analysis_task.delay(
        resume_bytes_b64, resume_file.filename, job_description_text, user_id
    )
    return TaskEnqueuedResponse(task_id=task.id)


@router.get("/tasks/{task_id}", response_model=TaskStatusResponse)
def get_task_status(task_id: str) -> TaskStatusResponse:
    async_result = celery_app.AsyncResult(task_id)

    if async_result.state == "FAILURE":
        return TaskStatusResponse(
            task_id=task_id, status="FAILURE", error=str(async_result.info)
        )
    if async_result.state == "SUCCESS":
        return TaskStatusResponse(
            task_id=task_id,
            status="SUCCESS",
            result=AnalysisResponse.model_validate(async_result.result),
        )
    return TaskStatusResponse(task_id=task_id, status=async_result.state)


@router.get("/{analysis_id}", response_model=AnalysisResponse)
def get_analysis(
    analysis_id: str,
    db: Session = Depends(get_db),
    current_user: Optional[UserRecord] = Depends(get_current_user_optional),
) -> AnalysisResponse:
    record = SQLAlchemyAnalysisRepository(db).get_by_id(analysis_id)
    if record is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Analysis not found.")
    if record.user_id is not None and (
        current_user is None or record.user_id != current_user.id
    ):
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not your analysis.")

    # AnalysisRecord deliberately stores scorecard/recommendations
    # directly rather than a full AnalysisResult (see its docstring in
    # app/application/ports.py) -- build the response schema straight
    # from those fields rather than constructing a fake AnalysisResult
    # with None resume/job_description just to satisfy
    # AnalysisResponse.from_domain's signature.
    return AnalysisResponse(
        resume_id=record.resume_id,
        job_description_id=record.job_description_id,
        scorecard=ScoreCardSchema.from_domain(record.scorecard),
        recommendations=[
            RecommendationSchema.from_domain(r) for r in record.recommendations
        ],
    )
