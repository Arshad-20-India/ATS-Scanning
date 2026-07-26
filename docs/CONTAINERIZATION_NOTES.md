# Containerization: What Was and Wasn't Verified Live

Being precise about this rather than implying more than what's true.

## The constraint

This project was built in a sandbox with no Docker daemon installed
(`docker: command not found`). That means `docker build` and
`docker compose up` could not be run live here. This is a different
category of limitation from the network restrictions in earlier
phases (Hugging Face, OpenAI, Google Fonts were all reachable-in-
principle services blocked by an egress allowlist; Docker is a
missing tool, not a blocked network call) — worth being clear about
the distinction.

## What WAS verified live, directly, in this sandbox

- **The backend's actual runtime commands.** Every `pip install` line
  in `backend/Dockerfile` (including the exact spaCy model wheel URL)
  is copy-identical to commands actually run and verified working in
  Phase 2 of this build.
- **The exact `alembic upgrade head` command** the entrypoint script
  runs — run for real against real Postgres in Phase 5, twice (dev and
  test databases).
- **The exact `uvicorn app.api.main:app` command** the Dockerfile's
  `CMD` uses — run for real as a live server in Phase 6, driven with
  real `curl` requests including a full register → login → analyze
  workflow.
- **The frontend's standalone build output**, byte for byte: `next
  build` was run in this sandbox with `output: "standalone"` enabled,
  and the *exact* directory assembly the Dockerfile's runtime stage
  performs (`COPY .next/standalone`, `COPY .next/static` into
  `.next/static`, `COPY public`) was manually replicated and then
  **actually started with `node server.js`** and hit with real `curl`
  requests (200 responses from `/`, `/login`, `/robots.txt`). This is
  the part of the frontend Dockerfile most likely to have a subtle
  path mistake (standalone output's directory layout is easy to get
  wrong), and it's the part that was checked most rigorously as a
  result. One real bug was caught this way during initial testing: a
  `cp *` glob silently excludes dotfiles/dot-directories in shells,
  which dropped `.next/standalone/.next` (containing `BUILD_ID` and
  the manifests the server needs) from a first verification attempt —
  not a Dockerfile bug (Docker's `COPY` on a named directory doesn't
  have this problem), but worth noting as exactly the kind of thing
  that's easy to get subtly wrong and only catches your attention when
  you actually run the assembled result.
- **Every file path referenced in both Dockerfiles and in
  `docker-compose.yml`** was cross-checked programmatically against
  the real repository structure (see the verification commands in the
  build history) — every `COPY` source and every `build.context`
  genuinely exists.
- **`docker-compose.yml`'s YAML syntax, service graph, and
  `depends_on` references** were validated with `yaml.safe_load` plus
  a script asserting every `depends_on` target is a real service name
  and every `build.context` path exists and contains a `Dockerfile`.
- **`.github/workflows/ci.yml`'s YAML syntax** was validated the same
  way.

## What was NOT verified live (and why that's a reasonable, disclosed gap)

- **`docker build` itself** for either image — no daemon available.
  The Dockerfiles are correct by construction (every command in them
  individually verified as above, every path cross-checked), but
  "every ingredient is verified" is not the same claim as "the
  assembled cake was baked and tasted." If you build these locally and
  hit an issue, the most likely category is a version-pin drift
  between when this was written and when you build (base image patch
  releases, etc.) — not a structural mistake in the Dockerfile logic.
- **`docker compose up`'s live orchestration** — the healthcheck
  timing, the `depends_on: condition: service_healthy` gating, the
  Celery worker actually picking up a task through the real Redis
  broker inside the Docker network. The equivalent orchestration
  *logic* (Postgres readiness before migrations, Redis availability
  before Celery, the Celery eager-mode task dispatch itself) was
  proven in Phase 5 and Phase 6 against real local Postgres/Redis
  processes — just not inside Docker's network namespace specifically.
- **The frontend Docker image's font loading** — `next/font/google`
  needs `fonts.googleapis.com` at build time; unreachable from this
  sandbox (see `frontend/README.md`). A real `docker build` with
  normal internet access will fetch these normally; this was worked
  around for local `next build` verification by temporarily swapping
  to system fonts, confirming that was the *only* remaining error, and
  restoring the real font-loading code before shipping — the same
  approach applies to a real Docker build.

## If you want to close this gap yourself

```bash
docker compose up --build
curl http://localhost:8000/health
curl http://localhost:3000/
```

If either fails, check `docker compose logs <service>` first — given
the verification above, the most likely causes are environment-specific
(base image version drift, platform architecture, or `.env` values not
set) rather than a structural error in these files.
