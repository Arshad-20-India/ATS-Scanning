"""
FastAPI dependency providers.

The ApplicationContainer (Phase 4) is built ONCE at app startup (see
main.py's lifespan handler) and stored on app.state -- not rebuilt per
request, since it holds the embedder/LLM provider which may hold
expensive model state or connection pools. DB sessions, by contrast,
are created fresh per request and closed at the end of it, which is
the standard FastAPI pattern for SQLAlchemy.
"""

from typing import Generator, Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.application.container import ApplicationContainer
from app.infrastructure.auth.security import InvalidTokenError, decode_access_token
from app.infrastructure.persistence.database import SessionLocal
from app.infrastructure.persistence.user_repository import UserRecord, UserRepository

_oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login", auto_error=False)


def get_db() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


def get_container(request: Request) -> ApplicationContainer:
    return request.app.state.container


def get_current_user(
    token: Optional[str] = Depends(_oauth2_scheme),
    db: Session = Depends(get_db),
) -> UserRecord:
    unauthorized = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if token is None:
        raise unauthorized

    try:
        user_id = decode_access_token(token)
    except InvalidTokenError as exc:
        raise unauthorized from exc

    user = UserRepository(db).get_by_id(user_id)
    if user is None:
        raise unauthorized
    return user


def get_current_user_optional(
    token: Optional[str] = Depends(_oauth2_scheme),
    db: Session = Depends(get_db),
) -> Optional[UserRecord]:
    """
    For endpoints that work anonymously but personalize/attribute data
    when a valid token IS supplied (e.g. analyze-without-signup stays
    possible, but a logged-in user's analyses get saved to their
    account).
    """
    if token is None:
        return None
    try:
        user_id = decode_access_token(token)
    except InvalidTokenError:
        return None
    return UserRepository(db).get_by_id(user_id)
