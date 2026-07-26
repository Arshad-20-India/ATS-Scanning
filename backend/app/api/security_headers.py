"""
Security headers middleware.

A deliberately small, defensible set -- each header addresses a
specific, real class of attack against an API + SPA pairing like this
one, not a checklist copied without understanding:

- X-Content-Type-Options: nosniff -- stops browsers from MIME-sniffing
  a response into executing as something other than what Content-Type
  says (relevant because file upload endpoints exist).
- X-Frame-Options: DENY -- prevents this API's /docs UI from being
  framed for clickjacking.
- Referrer-Policy: strict-origin-when-cross-origin -- avoids leaking
  full request paths (which can contain resume/analysis IDs) to
  third-party Referer headers.
- Permissions-Policy -- explicitly disables browser features this API
  has no legitimate use for.
- Strict-Transport-Security -- only meaningful over HTTPS (a reverse
  proxy/load balancer terminates TLS in front of this app in
  production); harmless to send always, browsers ignore it over plain
  HTTP.
"""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
        response.headers["Strict-Transport-Security"] = "max-age=63072000; includeSubDomains"
        return response
