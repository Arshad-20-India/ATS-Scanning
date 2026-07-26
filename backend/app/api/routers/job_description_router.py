from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_container, get_current_user, get_db
from app.api.schemas.job_description_schemas import (
    JobDescriptionCreateRequest,
    JobDescriptionResponse,
)
from app.application.container import ApplicationContainer
from app.infrastructure.persistence.job_description_repository import (
    SQLAlchemyJobDescriptionRepository,
)
from app.infrastructure.persistence.user_repository import UserRecord

router = APIRouter(prefix="/job-descriptions", tags=["job-descriptions"])


@router.post("", response_model=JobDescriptionResponse, status_code=status.HTTP_201_CREATED)
def create_job_description(
    body: JobDescriptionCreateRequest,
    container: ApplicationContainer = Depends(get_container),
    db: Session = Depends(get_db),
    current_user: UserRecord = Depends(get_current_user),
) -> JobDescriptionResponse:
    job_description = container.job_description_parser.parse(body.text)
    record = SQLAlchemyJobDescriptionRepository(db).save(
        job_description, user_id=current_user.id
    )
    return JobDescriptionResponse.from_domain(
        record.id, record.job_description, record.created_at
    )


@router.get("/{job_description_id}", response_model=JobDescriptionResponse)
def get_job_description(
    job_description_id: str,
    db: Session = Depends(get_db),
    current_user: UserRecord = Depends(get_current_user),
) -> JobDescriptionResponse:
    record = SQLAlchemyJobDescriptionRepository(db).get_by_id(job_description_id)
    if record is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Job description not found.")
    if record.user_id != current_user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Not your job description.")

    return JobDescriptionResponse.from_domain(
        record.id, record.job_description, record.created_at
    )


@router.get("", response_model=List[JobDescriptionResponse])
def list_my_job_descriptions(
    db: Session = Depends(get_db),
    current_user: UserRecord = Depends(get_current_user),
) -> List[JobDescriptionResponse]:
    records = SQLAlchemyJobDescriptionRepository(db).list_by_user(current_user.id)
    return [
        JobDescriptionResponse.from_domain(r.id, r.job_description, r.created_at)
        for r in records
    ]
