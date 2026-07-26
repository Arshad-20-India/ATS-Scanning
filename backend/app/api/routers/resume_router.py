"""
Standalone resume upload/retrieval, decoupled from analysis. Useful
for a product flow where a candidate uploads and reviews their parsed
resume (ATS-compatibility feedback, etc.) before matching it against
any specific job description -- see AnalysisResult's design in Phase 4
for why matching is a separate concern from parsing.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_container, get_current_user, get_db
from app.api.schemas.resume_schemas import ResumeResponse
from app.application.container import ApplicationContainer
from app.core.config import settings
from app.infrastructure.persistence.resume_repository import SQLAlchemyResumeRepository
from app.infrastructure.persistence.user_repository import UserRecord

router = APIRouter(prefix="/resumes", tags=["resumes"])


@router.post("", response_model=ResumeResponse, status_code=status.HTTP_201_CREATED)
async def upload_resume(
    file: UploadFile = File(...),
    container: ApplicationContainer = Depends(get_container),
    db: Session = Depends(get_db),
    current_user: UserRecord = Depends(get_current_user),
) -> ResumeResponse:
    file_bytes = await file.read()
    if len(file_bytes) > settings.max_upload_size_bytes:
        raise HTTPException(
            status.HTTP_413_CONTENT_TOO_LARGE,
            f"File exceeds the {settings.max_upload_size_bytes // (1024 * 1024)}MB upload limit.",
        )
    resume = container.resume_parser.parse(file_bytes, file.filename)

    record = SQLAlchemyResumeRepository(db).save(
        resume, filename=file.filename, user_id=current_user.id
    )
    return ResumeResponse.from_domain(
        record.id, record.resume, record.filename, record.created_at
    )


@router.get("/{resume_id}", response_model=ResumeResponse)
def get_resume(
    resume_id: str,
    db: Session = Depends(get_db),
    current_user: UserRecord = Depends(get_current_user),
) -> ResumeResponse:
    record = SQLAlchemyResumeRepository(db).get_by_id(resume_id)
    if record is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Resume not found.")
    if record.user_id != current_user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not your resume.")

    return ResumeResponse.from_domain(
        record.id, record.resume, record.filename, record.created_at
    )


@router.get("", response_model=List[ResumeResponse])
def list_my_resumes(
    db: Session = Depends(get_db),
    current_user: UserRecord = Depends(get_current_user),
) -> List[ResumeResponse]:
    records = SQLAlchemyResumeRepository(db).list_by_user(current_user.id)
    return [
        ResumeResponse.from_domain(r.id, r.resume, r.filename, r.created_at)
        for r in records
    ]


from pydantic import BaseModel

class RewriteRequest(BaseModel):
    job_description_text: str

@router.post("/rewrite")
async def rewrite_resume(
    request: RewriteRequest,
    resume_file: UploadFile = File(...),
    container: ApplicationContainer = Depends(get_container),
) -> dict:
    file_bytes = await resume_file.read()
    analysis_result = container.analyze_resume_use_case.execute(
        file_bytes, resume_file.filename, request.job_description_text
    )
    rewritten_text = container.rewrite_resume_use_case.execute(
        analysis_result.resume,
        analysis_result.job_description,
        analysis_result.recommendations,
    )
    return {
        "rewritten_text": rewritten_text,
        "scorecard": analysis_result.scorecard,
        "recommendations": analysis_result.recommendations,
    }
