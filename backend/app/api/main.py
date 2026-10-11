"""
FastAPI application factory.

`create_app()` rather than a bare module-level `app = FastAPI()` so
tests can construct independent app instances with different
containers injected (see tests/unit/api/conftest.py) without needing
environment-variable gymnastics or monkeypatching a shared singleton.
"""

import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.api.errors import register_exception_handlers
from app.api.health import check_readiness
from app.api.metrics import instrument_app
from app.api.middleware import RequestLoggingMiddleware
from app.api.rate_limit import limiter
from app.api.routers import analysis_router, auth_router, job_description_router, resume_router
from app.api.security_headers import SecurityHeadersMiddleware
from app.application.container import ApplicationContainer, build_container
from app.core.config import settings
from app.core.logging import configure_logging

logger = logging.getLogger(__name__)

_INSECURE_DEFAULT_JWT_SECRET = "dev-only-insecure-secret-change-in-production"


class InsecureConfigurationError(RuntimeError):
    """Raised at startup if a production deployment is misconfigured in a way
    that would be a real security hole -- fail fast and loud, not a warning
    buried in logs someone might not read."""


def create_app(container: Optional[ApplicationContainer] = None) -> FastAPI:
    configure_logging()

    if settings.jwt_secret_key == _INSECURE_DEFAULT_JWT_SECRET:
        if settings.is_production():
            raise InsecureConfigurationError(
                "ENVIRONMENT=production but JWT_SECRET_KEY is still the "
                "insecure development default. Set a real secret via the "
                "JWT_SECRET_KEY environment variable before deploying. "
                "Generate one with: python3 -c \"import secrets; "
                "print(secrets.token_urlsafe(48))\""
            )
        logger.warning(
            "JWT_SECRET_KEY is using the insecure development default. "
            "Set a real secret via the JWT_SECRET_KEY environment variable "
            "before deploying."
        )

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Built once per process (see ApplicationContainer's docstring
        # in Phase 4 -- it may hold expensive model/connection state).
        app.state.container = container or build_container()
        logger.info(
            "Application container built; startup complete. environment=%s",
            settings.environment,
        )
        yield
        logger.info("Shutting down.")

    app = FastAPI(
        title="AI Resume Intelligence Scanner",
        description=(
            "Explainable, evidence-based resume evaluation. Every score "
            "returned by this API is backed by an Evidence[] list -- see "
            "the /analyses endpoints' response schema."
        ),
        version="0.1.0",
        lifespan=lifespan,
    )

    # Rate limiting (Phase 9) -- see app/api/rate_limit.py for why this
    # is Redis-backed rather than slowapi's default in-memory store.
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(RequestLoggingMiddleware)

    cors_origins = [o for o in settings.cors_origins_list() if o != "*"]
    for default_origin in [
        "https://ats-scanning.vercel.app",
        "http://localhost:3000",
        "http://localhost:8000",
    ]:
        if default_origin not in cors_origins:
            cors_origins.append(default_origin)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=cors_origins,
        allow_origin_regex=r"^https?://.*",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["*"],
    )

    register_exception_handlers(app)
    instrument_app(app)  # exposes /metrics

    api_prefix = "/api/v1"
    app.include_router(auth_router.router, prefix=api_prefix)
    app.include_router(resume_router.router, prefix=api_prefix)
    app.include_router(job_description_router.router, prefix=api_prefix)
    app.include_router(analysis_router.router, prefix=api_prefix)

    @app.get("/health", tags=["health"])
    def health() -> dict:
        """Liveness: is the process alive at all? Zero dependencies, by design."""
        return {"status": "ok"}

    @app.get("/health/ready", tags=["health"])
    def readiness(db: Session = Depends(get_db)) -> dict:
        """Readiness: can this instance actually serve real traffic right now?"""
        result = check_readiness(db)
        status_code = 200 if result.ready else 503
        from fastapi.responses import JSONResponse

        return JSONResponse(
            status_code=status_code,
            content={"ready": result.ready, "checks": result.checks},
        )

    return app


app = create_app()
