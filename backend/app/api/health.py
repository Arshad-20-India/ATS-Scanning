"""
Readiness vs. liveness, the standard distinction (Kubernetes-style,
but useful for any orchestrator or load balancer):

- Liveness (`GET /health`, unchanged since Phase 6): "is the process
  alive and able to respond at all?" Deliberately has zero
  dependencies -- if this fails, the orchestrator should restart the
  container. It must never fail just because Postgres is briefly slow.
- Readiness (`GET /health/ready`, this module): "is this instance
  actually able to serve real traffic right now?" Pings Postgres and
  Redis with a short timeout. If this fails, a load balancer should
  stop routing new traffic here (without necessarily restarting the
  container) -- e.g. during a database failover.
"""

from __future__ import annotations

from dataclasses import dataclass

import redis
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings


@dataclass(frozen=True)
class ReadinessResult:
    ready: bool
    checks: dict[str, bool]


def check_readiness(db: Session) -> ReadinessResult:
    checks = {
        "database": _check_database(db),
        "redis": _check_redis(),
    }
    return ReadinessResult(ready=all(checks.values()), checks=checks)


def _check_database(db: Session) -> bool:
    try:
        db.execute(text("SELECT 1"))
        return True
    except Exception:  # noqa: BLE001 -- any DB error means "not ready", not a crash
        return False


def _check_redis() -> bool:
    try:
        client = redis.from_url(settings.redis_url, socket_connect_timeout=2)
        return bool(client.ping())
    except Exception:  # noqa: BLE001 -- any Redis error means "not ready", not a crash
        return False
