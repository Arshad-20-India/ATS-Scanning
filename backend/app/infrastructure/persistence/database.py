"""
Database engine and session management.

Synchronous SQLAlchemy (psycopg2), not async: a deliberate, documented
trade-off. Phase 8 introduces Celery for background analysis jobs,
and Celery workers are synchronous by default -- using sync SQLAlchemy
everywhere avoids maintaining two different DB access patterns (async
for the API, sync for workers). FastAPI (Phase 6) handles sync DB
calls fine via its threadpool for regular endpoints; if a specific
endpoint's DB load ever became a bottleneck, that single endpoint
could move to asyncpg without changing this module's contract for
everyone else.
"""

from __future__ import annotations

from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    pass


def create_session_factory(database_url: str | None = None) -> sessionmaker[Session]:
    engine = create_engine(database_url or settings.database_url, pool_pre_ping=True)
    return sessionmaker(bind=engine, autoflush=False, autocommit=False)


# Module-level default factory, built from settings. Tests and other
# call sites that need a different database (e.g. a test database)
# should call create_session_factory(...) directly rather than rely
# on this module-level instance.
SessionLocal = create_session_factory()


def get_session() -> Generator[Session, None, None]:
    """FastAPI-dependency-shaped generator (Phase 6 will use this directly)."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
