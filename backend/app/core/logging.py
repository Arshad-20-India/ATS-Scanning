"""
Logging setup shared by the API process and Celery workers.

Deliberately simple: structured-enough (timestamp, level, logger name,
message) to be useful in any log aggregator without adding a
dependency (structlog, python-json-logger) this project doesn't yet
need. Phase 9 (observability) is where metrics/tracing get added; this
is the logging foundation that phase builds on, not a replacement for it.
"""

from __future__ import annotations

import logging
import sys


def configure_logging(level: int = logging.INFO) -> None:
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Avoid duplicate handlers if configure_logging() is called more
    # than once (e.g. once by the API, once by a test fixture).
    if root_logger.handlers:
        return

    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )
    handler.setFormatter(formatter)
    root_logger.addHandler(handler)

    # Quiet noisy third-party loggers down to WARNING by default.
    for noisy_logger in ("uvicorn.access", "sqlalchemy.engine"):
        logging.getLogger(noisy_logger).setLevel(logging.WARNING)
