"""
Celery application instance.

Broker and result backend both point at Redis (a different DB index
than the app cache, see settings.celery_broker_url) -- no separate
message broker (RabbitMQ etc) needed for this scale. task_track_started
is enabled so a client polling task status can distinguish "queued"
from "actually running" rather than only seeing PENDING until it's
fully done.
"""

from __future__ import annotations

from celery import Celery

from app.core.config import settings

celery_app = Celery(
    "resume_scanner",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=["app.infrastructure.tasks.analysis_tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    task_track_started=True,
    result_expires=60 * 60 * 24,  # 24h
)
