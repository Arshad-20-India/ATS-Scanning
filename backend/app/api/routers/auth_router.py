from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.dependencies import get_current_user, get_db
from app.api.rate_limit import limiter
from app.api.schemas.auth_schemas import (
    TokenResponse,
    UserRegisterRequest,
    UserResponse,
)
from app.core.config import settings
from app.infrastructure.auth.security import create_access_token, verify_password, hash_password
from app.infrastructure.persistence.user_repository import UserRecord, UserRepository

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit(settings.rate_limit_auth)
def register(request: Request, body: UserRegisterRequest, db: Session = Depends(get_db)) -> UserResponse:
    repo = UserRepository(db)
    if repo.get_by_email(body.email) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="An account with this email already exists.",
        )

    record = repo.create(
        email=body.email,
        hashed_password=hash_password(body.password),
        full_name=body.full_name,
    )
    return UserResponse(
        id=record.id,
        email=record.email,
        full_name=record.full_name,
        created_at=record.created_at,
    )


@router.post("/login", response_model=TokenResponse)
@limiter.limit(settings.rate_limit_auth)
def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(OAuth2PasswordRequestForm), db: Session = Depends(get_db)
) -> TokenResponse:
    # OAuth2PasswordRequestForm's "username" field carries the email --
    # this is the standard OAuth2 password-flow field name, reused
    # here rather than inventing a non-standard form shape.
    repo = UserRepository(db)
    user = repo.get_by_email(form_data.username)

    invalid_credentials = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if user is None or not verify_password(form_data.password, user.hashed_password):
        raise invalid_credentials

    token = create_access_token(subject=user.id)
    return TokenResponse(access_token=token)


@router.get("/me", response_model=UserResponse)
def get_me(current_user: UserRecord = Depends(get_current_user)) -> UserResponse:
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        created_at=current_user.created_at,
    )
