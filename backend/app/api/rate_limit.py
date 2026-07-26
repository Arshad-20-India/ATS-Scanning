"""
Rate limiting.

Backed by Redis (not slowapi's default in-memory store) specifically
because this API runs as multiple uvicorn worker processes in
production -- an in-memory limiter would let each process enforce its
own separate quota, silently multiplying the effective limit by the
worker count. Using the same Redis instance already deployed for
caching (Phase 5) and Celery (Phase 6) keeps the limit correct
regardless of worker count.

Two tiers are applied at the router level (see auth_router.py,
analysis_router.py):
  - Auth endpoints get a tight limit (settings.rate_limit_auth) --
    the classic brute-force-login defense.
  - Analysis endpoints get a moderate limit (settings.rate_limit_analysis)
    -- these are the expensive ones (parsing + embedding + optionally
    an LLM call), so they're the ones worth protecting from abuse.
  - Everything else gets settings.rate_limit_default as a blanket floor.
"""

from __future__ import annotations

from slowapi import Limiter
from slowapi.util import get_remote_address

from app.core.config import settings

limiter = Limiter(
    key_func=get_remote_address,
    storage_uri=settings.redis_url,
    default_limits=[settings.rate_limit_default],
    # Tests run many requests from the same client in quick succession
    # by design (that's what makes them fast) -- real rate limiting
    # would make the test suite itself flaky/order-dependent against
    # real Redis-backed state. Disabled via RATE_LIMIT_ENABLED=false in
    # the test environment (see tests/unit/api/conftest.py); on by
    # default everywhere else.
    enabled=settings.rate_limit_enabled,
)
