# Security

A honest account of what's actually implemented, not a checklist
implying more than what's true.

## Authentication

- Passwords hashed with `bcrypt` directly (not `passlib`, which has a
  confirmed real incompatibility with `bcrypt` >= 4.0's changed API —
  see `backend/README.md`'s Phase 6 section for the exact error this
  build hit and fixed).
- JWTs (`python-jose`, HS256), 60-minute expiry by default
  (`JWT_ACCESS_TOKEN_EXPIRE_MINUTES`).
- **Fail-fast in production**: if `ENVIRONMENT=production` and
  `JWT_SECRET_KEY` is still the insecure development default, the app
  refuses to start (`InsecureConfigurationError`, `app/api/main.py`) —
  not a warning buried in logs someone might not read. In
  `development`, it's a warning, since local dev without a real secret
  is a normal, safe thing to do.

## Rate limiting

Redis-backed (`slowapi`), not in-memory — deliberately, because this
API runs as multiple `uvicorn` worker processes in production, and an
in-memory limiter would let each process enforce its own separate
quota (silently multiplying the effective limit by worker count). Two
tiers:

- **Auth endpoints** (`/auth/register`, `/auth/login`):
  `RATE_LIMIT_AUTH`, default `10/minute` — the standard brute-force-
  login defense.
- **Analysis endpoints** (`/analyses/sync`, `/analyses/async`):
  `RATE_LIMIT_ANALYSIS`, default `20/minute` — these are the expensive
  ones (parsing + embedding + optionally an LLM call), so they're the
  ones most worth protecting from abuse or accidental cost blowout.
- Everything else: `RATE_LIMIT_DEFAULT`, `120/minute`, as a blanket
  floor.

Verified with a real, live server: 10 rapid-fire registration requests
succeeded, the 11th through 13th got real `429` responses — see
`docs/PERFORMANCE.md` for the actual captured output.

## Upload limits

Both resume-upload endpoints (`/resumes`, `/analyses/sync`,
`/analyses/async`) reject files over `MAX_UPLOAD_SIZE_BYTES` (default
10MB) with `413`, checked before the file is handed to any parser —
not a theoretical DoS vector left open.

## Security headers

Applied to every response (`app/api/security_headers.py`), each
addressing a specific real risk for an API + SPA pairing like this
one — see that file's docstring for the reasoning behind each header
(`X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`,
`Permissions-Policy`, `Strict-Transport-Security`). Not a generic
checklist copy-paste; every header there is explained in terms of what
it actually defends against in this specific application.

## CORS

Configurable via `CORS_ALLOWED_ORIGINS` (comma-separated), defaulting
to `*` for local development. **Set this to your real frontend
domain(s) before deploying to production** — `.env.example` calls this
out explicitly.

## What's explicitly NOT done here (disclosed, not hidden)

- **No refresh tokens** — a single JWT with a fixed expiry. A
  production-hardening pass would add refresh token rotation; noted
  as a real gap, not silently worked around.
- **No email verification on registration.** Any syntactically valid
  email can register. Fine for this project's current scope; a real
  product would add verification before certain actions.
- **No account lockout after repeated failed logins** beyond the rate
  limiter's per-IP throttling — an attacker distributed across many
  IPs isn't slowed by this. A production hardening pass would add
  per-account (not just per-IP) failed-login tracking.
- **CORS defaults to `*`** — safe for local dev, actively wrong for
  production if left unchanged. Called out above and in
  `.env.example`, not hidden in a config file no one reads.
- **No dependency vulnerability scanning wired into CI** (e.g.
  `pip-audit`, `npm audit` as a CI gate rather than a manual check) —
  a reasonable next addition, not currently automated.

Being explicit about these is the point: a security section that
lists only what's done and never what's missing isn't trustworthy.
