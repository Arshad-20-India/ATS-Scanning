"""
Centralized exception handling.

Every error response has the same shape: {"error": {"code": str,
"message": str}}. This is what "comprehensive error handling" means in
practice for an API: a predictable contract the frontend can branch on
by `code`, not by parsing prose out of `message`.

Handlers here catch exceptions that legitimately escape the use-case
layer (e.g. a genuinely malformed upload). They do NOT catch
UngroundedResponseError (Phase 3) -- that's already handled inside
GenerateRecommendationsUseCase (Phase 4) and should never reach here;
if it does, that's a real bug and the generic 500 handler is correct
for it (loud failure, not a silent 200).
"""

from __future__ import annotations

import logging

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from app.infrastructure.parsing.resume_parser import UnsupportedFileTypeError

logger = logging.getLogger(__name__)


def _error_response(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={"error": {"code": code, "message": message}},
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(UnsupportedFileTypeError)
    async def _unsupported_file_type(request: Request, exc: UnsupportedFileTypeError):
        return _error_response(
            status.HTTP_400_BAD_REQUEST, "unsupported_file_type", str(exc)
        )

    @app.exception_handler(RequestValidationError)
    async def _validation_error(request: Request, exc: RequestValidationError):
        return _error_response(
            status.HTTP_422_UNPROCESSABLE_CONTENT,
            "validation_error",
            "; ".join(
                f"{'.'.join(str(p) for p in e['loc'])}: {e['msg']}"
                for e in exc.errors()
            ),
        )

    @app.exception_handler(IntegrityError)
    async def _integrity_error(request: Request, exc: IntegrityError):
        logger.warning("Database integrity error", exc_info=True)
        return _error_response(
            status.HTTP_409_CONFLICT,
            "conflict",
            "The request conflicts with existing data (e.g. duplicate email).",
        )

    @app.exception_handler(ValueError)
    async def _value_error(request: Request, exc: ValueError):
        return _error_response(status.HTTP_400_BAD_REQUEST, "bad_request", str(exc))

    @app.exception_handler(Exception)
    async def _unhandled_exception(request: Request, exc: Exception):
        logger.error("Unhandled exception", exc_info=True)
        return _error_response(
            status.HTTP_500_INTERNAL_SERVER_ERROR,
            "internal_error",
            "An unexpected error occurred.",
        )
