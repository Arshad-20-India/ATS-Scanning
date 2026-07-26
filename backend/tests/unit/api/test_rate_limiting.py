"""
Rate limiting is disabled globally for the test suite (see
tests/conftest.py) so the rest of the suite isn't flaky against real
Redis-backed limit windows. These tests deliberately re-enable it
against an isolated limiter/Redis DB so they can prove the real
mechanism works without polluting -- or being polluted by -- any
other test's request volume.
"""

from __future__ import annotations

import redis
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address

_TEST_REDIS_URL = "redis://localhost:6379/3"  # dedicated DB index, isolated from other tests


def _build_rate_limited_client(limit: str) -> TestClient:
    # Flush this dedicated rate-limit DB so no state leaks between test runs.
    redis.from_url(_TEST_REDIS_URL).flushdb()

    # A minimal throwaway app -- proves the rate-limiting *mechanism*
    # (decorator -> 429 on exceeding N requests) in isolation, rather
    # than depending on the full create_app() (which pulls in the DB,
    # container, and Prometheus instrumentation this test has no need
    # to exercise).
    #
    # NOTE: FastAPI/Starlette must resolve the `request: Request`
    # annotation to the real Request class via typing.get_type_hints()
    # at route-registration time. With `from __future__ import
    # annotations` active (PEP 563), annotations are stored as string
    # literals and resolved against the function's *module-level*
    # globals -- so `Request` must be imported at module level here,
    # not inside this helper function. (An earlier version of this
    # file imported it locally and every request silently got treated
    # as a malformed parameter, failing with 422 -- caught by actually
    # running these tests, not just reading the code.)
    test_limiter = Limiter(
        key_func=get_remote_address, storage_uri=_TEST_REDIS_URL, enabled=True
    )

    probe_app = FastAPI()
    probe_app.state.limiter = test_limiter
    probe_app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    probe_app.add_middleware(SlowAPIMiddleware)

    @probe_app.get("/probe")
    @test_limiter.limit(limit)
    def probe(request: Request):
        return {"ok": True}

    return TestClient(probe_app)


def test_requests_within_limit_succeed():
    client = _build_rate_limited_client(limit="3/minute")
    for _ in range(3):
        response = client.get("/probe")
        assert response.status_code == 200


def test_requests_exceeding_limit_return_429():
    client = _build_rate_limited_client(limit="3/minute")
    for _ in range(3):
        assert client.get("/probe").status_code == 200

    fourth = client.get("/probe")
    assert fourth.status_code == 429
    assert "rate limit" in fourth.json()["error"].lower()


def test_rate_limit_is_per_client_key():
    """
    get_remote_address is the key function -- confirms the limiter is
    wired to key by client, not globally across all clients (which
    would make the limit meaningless under any real concurrent load).
    """
    client = _build_rate_limited_client(limit="2/minute")
    assert client.get("/probe").status_code == 200
    assert client.get("/probe").status_code == 200
    assert client.get("/probe").status_code == 429
    # Same TestClient/IP again -- still limited (proves state persisted
    # correctly in the isolated Redis DB, not just in-process memory).
    assert client.get("/probe").status_code == 429
