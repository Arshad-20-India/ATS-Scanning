# AI Resume Intelligence Scanner

An explainable, evidence-based resume evaluation platform. Every score
is derived from measurable criteria and shipped with the exact
evidence that produced it — never an arbitrary number, never an
unexplained recommendation.

## Quick start (Docker Compose)

```bash
cp .env.example .env
# edit .env: set a real JWT_SECRET_KEY, and OPENAI_API_KEY if you want
# LLM-generated recommendations (the system works fully without one --
# see "LLM fallback" below)

docker compose up --build
```

- Frontend: http://localhost:3000
- API docs: http://localhost:8000/docs

> **Note on this repository's provenance**: every phase below was
> built with a real running instance at each step — real PostgreSQL,
> real Redis, a real live `uvicorn` server driven with `curl`, the
> actual product flow driven through a real Chromium browser via
> Playwright (screenshots included in the delivery), and Phase 9's
> rate limiting, security headers, and readiness checks all verified
> against a live server too (see `docs/PERFORMANCE.md` for the
> captured output, including a real 429 response after exactly the
> configured rate limit). The two external services this project
> depends on that couldn't be exercised live here — Hugging Face
> (embedding model weights) and OpenAI (LLM calls) — are both built
> with injectable adapters specifically so they're fully unit-tested
> without live network access, and work unchanged the moment they're
> deployed anywhere with normal internet access. Docker itself isn't
> installed in the sandbox this was built in either; the Dockerfiles
> and compose file were verified as precisely as possible without a
> daemon — see `docs/CONTAINERIZATION_NOTES.md` for exactly what was
> and wasn't verified live.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Frontend (Next.js / React / TypeScript / Tailwind v4)       │
└───────────────────────────┬───────────────────────────────────┘
                             │ REST (JWT auth)
┌───────────────────────────▼───────────────────────────────────┐
│  API (FastAPI)                                                 │
│  ┌────────────────────────────────────────────────────────┐   │
│  │  Application layer -- use cases, DI container           │   │
│  │  ┌──────────────────────────────────────────────────┐  │   │
│  │  │  Domain layer -- entities, ScoringEngine,          │  │   │
│  │  │  ICategoryScorer implementations, ports (ABCs)      │  │   │
│  │  │  ZERO framework dependencies, fully unit-tested     │  │   │
│  │  └──────────────────────────────────────────────────┘  │   │
│  │  Infrastructure -- implements domain/application ports: │   │
│  │  spaCy/pdfplumber/python-docx parsers, Sentence-         │   │
│  │  Transformers embedder, OpenAI LLM adapter, SQLAlchemy   │   │
│  │  repositories, Redis cache, Celery tasks                 │   │
│  └────────────────────────────────────────────────────────┘   │
└─────┬──────────────────┬──────────────────┬───────────────────┘
      │                  │                  │
┌─────▼─────┐      ┌─────▼─────┐     ┌──────▼──────┐
│ PostgreSQL │      │   Redis    │     │ Celery worker │
│ (JSONB)    │      │(cache+queue)│    │ (async analysis)│
└────────────┘      └────────────┘     └───────────────┘
```

This is Clean Architecture, enforced structurally, not just by
convention: the domain layer imports nothing from infrastructure or
the API; the application layer imports domain but not infrastructure
implementations directly (only their port/interface definitions);
infrastructure is the only layer that imports concrete third-party
libraries. `app/application/container.py` is the single composition
root where concrete adapters get wired to abstract ports.

## The core rule that shapes the whole system

**No score, and no recommendation, exists without the `Evidence[]`
that produced it.** This is enforced structurally, not by convention
— see `backend/README.md`'s "Domain Layer" section for exactly how
(`ICategoryScorer` → shared `aggregate_evidence()`, `ILLMProvider`
methods that require `Evidence` as input and can't originate a score,
`MatchingPolicy` wrapping every similarity score in an `Evidence`
before it's returned).

## LLM fallback

Recommendations work with **or without** an `OPENAI_API_KEY`. If none
is configured, `GenerateRecommendationsUseCase` (Phase 4) falls back
to deterministic, template-built messages straight from each failing
`Evidence` — the user always gets a traceable recommendation. See
`backend/README.md`'s Phase 4 section for the reasoning and the test
that proves it (`test_llm_failure_falls_back_to_template_never_raises`).

## Project structure

```
backend/    FastAPI + Celery + SQLAlchemy -- see backend/README.md
frontend/   Next.js + React + TypeScript  -- see frontend/README.md
            (frontend/DESIGN.md has the visual design rationale)
docs/       Cross-cutting notes (this containerization phase's
            verification limits, etc.)
docker-compose.yml, backend/Dockerfile, frontend/Dockerfile
.github/workflows/ci.yml
```

## Build phases (in the order they were actually built and verified)

| Phase | What | Tests |
|---|---|---|
| 1 | Domain layer (entities, scoring engine, ports) | 33 |
| 2 | Parsing & NLP (PDF/DOCX, spaCy, embeddings) | 56 |
| 3 | LLM provider (OpenAI, grounding validation) | 21 |
| 4 | Application layer (use cases, DI container) | 19 |
| 5 | Persistence (PostgreSQL, Redis) | 32 |
| 6 | API (FastAPI, JWT auth, Celery) | 29 |
| 7 | Frontend (Next.js dashboard) | verified via `tsc`/`eslint`/`next build`/Playwright |
| 8 | Containerization (Docker, Compose, CI) | see `docs/CONTAINERIZATION_NOTES.md` |
| 9 | Observability & hardening (metrics, rate limiting, security) | 17 |

**All 9 phases complete. 208 backend tests, 95% coverage**, run
against real PostgreSQL and Redis instances throughout — see
`backend/README.md` for the full per-phase breakdown, including six
real bugs (across the whole build) that were caught and fixed by
actually running things rather than just writing them.

## Further documentation

- `docs/OBSERVABILITY.md` — health checks, metrics, what's exposed and why
- `docs/SECURITY.md` — auth, rate limiting, upload limits, and an
  honest list of what's deliberately *not* hardened yet
- `docs/PERFORMANCE.md` — real measured latency/throughput numbers,
  reproducible with `scripts/load_test.py`
- `docs/CONTAINERIZATION_NOTES.md` — precisely what was and wasn't
  verified live for the Docker setup, given no daemon in the build sandbox
- `backend/README.md` / `frontend/README.md` — per-side setup and
  architecture detail
- `frontend/DESIGN.md` — the visual design rationale

## Running without Docker

See `backend/README.md`'s "Running Everything Locally" section and
`frontend/README.md`'s "Setup" section for running each side directly
(useful for active development, where Docker's build-and-restart cycle
is slower than a hot-reloading dev server).
