# Resume Scanner — Backend

## Phase 1: Domain Layer ✅

Pure Python, zero framework dependencies, fully unit-tested. See
"Domain Layer" section below (unchanged from Phase 1).

## Phase 2: Infrastructure — Parsing & NLP ✅

Implements the domain ports (`IResumeParser`, `IJobDescriptionParser`,
`IEmbedder`) with real libraries: pdfplumber, python-docx, spaCy, and
sentence-transformers.

```
app/infrastructure/
├── parsing/
│   ├── raw_document.py          # shared RawDocument(text, formatting_flags)
│   ├── pdf_extractor.py         # pdfplumber: text + ATS structural flags
│   ├── docx_extractor.py        # python-docx: text + ATS structural flags
│   ├── section_detector.py      # header-line detection -> {section: body_text}
│   ├── contact_extractor.py     # regex (email/phone/linkedin) + spaCy NER (name)
│   ├── date_extractor.py        # deterministic date-range parsing
│   ├── skills_extractor.py      # Skills section -> Skill[] (via SkillNormalizer)
│   ├── experience_extractor.py  # Experience section -> ExperienceEntry[]
│   ├── education_extractor.py   # Education section -> EducationEntry[]
│   ├── certification_extractor.py
│   ├── project_extractor.py
│   ├── grammar_checker.py       # spaCy dep-parse passive voice + rule heuristics
│   ├── resume_parser.py         # IResumeParser impl -- orchestrates the above
│   └── job_description_parser.py # IJobDescriptionParser impl
└── nlp/
    ├── spacy_pipeline.py        # singleton model loader
    └── sentence_transformer_embedder.py  # IEmbedder impl
```

### Setup

```bash
pip install -r requirements.txt
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl
```

### Running tests

```bash
pip install -r requirements-dev.txt
pytest tests/ -v --cov=app --cov-report=term-missing
```

**90 tests, 95% coverage.** Domain tests (Phase 1) use hand-written
fakes; infrastructure tests (Phase 2) run against *real* DOCX/PDF
bytes generated on the fly (via `python-docx` and `fpdf2`) and a real
loaded spaCy model — not mocks — so they prove the actual parsing
logic works, not just that functions were called.

### A note on the Sentence-Transformers adapter

`SentenceTransformerEmbedder` downloads real model weights from
Hugging Face on first use in a normal deployment. It is built with
constructor-injected model support specifically so it can be unit
tested (see `test_sentence_transformer_embedder.py`) without that
network dependency — the same pattern Phase 1 used for `FakeEmbedder`.
No code changes are needed to use it for real; just don't pass a
`model=` argument and it lazy-loads `all-MiniLM-L6-v2` (configurable
via `SENTENCE_TRANSFORMER_MODEL` env var) on first call.

### Known, documented limitations (not bugs — deliberate scope boundaries)

- **PDF text-box / column-layout detection is approximate.** True
  vector-object-graph analysis is out of scope for now; see
  `pdf_extractor.py` docstring.
- **DOCX page count defaults to 1** — accurate page count needs
  rendering (LibreOffice/docx2pdf), deliberately not added as a
  dependency yet.
- **Grammar checking is rule-based, not LanguageTool.** Avoids a JVM
  + large model dependency; the output shape (`GrammarFinding`,
  `WritingMetrics`) is decoupled from *how* it's computed, so swapping
  in LanguageTool later touches only `grammar_checker.py`.
- **JD skill extraction is section-header-driven.** A JD with no
  recognizable "Required"/"Preferred" headers will yield empty skill
  lists rather than guessing — consistent with Phase 1's "absence of a
  requirement is scored as a pass, not a failure" principle.

### Bugs found and fixed during real end-to-end testing

Worth noting since it's why the sandbox testing loop mattered:
1. **Experience header layout**: initial version assumed title/company
   and the date range were always on the same line; real resumes
   commonly split them across two lines. Fixed with
   `looks_like_date_only()` + two-pass header detection.
2. **Date-range hyphen ambiguity**: `"01-2021"` (single date) and
   `"2021-2023"` (range) both use `-`, which broke naive splitting.
   Fixed by restricting the single-date month/year separator to `/`
   only, making a bare hyphen unambiguous.
3. **JD "Required"/"Preferred" bare headers**: initial patterns only
   matched "Required Skills"/"Requirements", not the bare word
   "Required" alone (very common in real postings). Fixed.
4. **JD skill/requirement conflation**: a JD's "Required" section
   commonly mixes skill bullets with years-of-experience and degree
   bullets under one header; these were being misclassified as skill
   names. Fixed by filtering lines that match the years/degree
   patterns out of the skill list.

All four were caught by running the *actual* parsers against
generated file fixtures and inspecting output, not by inspection of
the code alone — which is exactly why this phase was built with a
tight test-and-verify loop rather than shipped in one pass.

---

## Phase 3: LLM Provider (OpenAI) ✅

Implements `ILLMProvider` with a real OpenAI-backed adapter, plus two
defense-in-depth layers to keep generated text grounded in `Evidence`:

```
app/infrastructure/llm/
├── prompt_templates.py     # explicit "don't invent facts" system+user prompts
├── response_validator.py   # programmatic check: every number in the
│                            # response must trace back to an Evidence value
│                            # (including 0.4 <-> "40%" percentage equivalence)
├── openai_provider.py      # OpenAIProvider(ILLMProvider): generate -> validate
│                            # -> retry once with a stricter prompt if ungrounded
│                            # -> raise UngroundedResponseError if still ungrounded
└── provider_factory.py     # get_llm_provider(): single seam for adding
                             # Anthropic / local providers later
```

### The three-layer grounding guarantee

1. **Structural** (Phase 1, unchanged): `ILLMProvider` methods require
   `Evidence` as input and return only `str` — there is no method that
   lets an LLM originate a score.
2. **Prompted**: every system prompt explicitly forbids introducing
   facts, numbers, or claims absent from the supplied evidence.
3. **Verified**: `response_validator.is_grounded()` checks every
   number in the generated text against the evidence's `found_value`/
   `expected_value` (with percentage-ratio equivalence handled). If a
   response fails this check, `OpenAIProvider` retries once with a
   stricter prompt; if it still fails, it raises
   `UngroundedResponseError` rather than silently returning a
   possibly-fabricated explanation. The Phase 4 use case layer is
   expected to catch this and fall back to a template-based
   explanation, not surface nothing.

No layer alone is airtight (layer 3 only checks numeric claims, not
qualitative ones), but together they make fabrication both hard to
produce and cheap to catch.

### Setup

```bash
pip install -r requirements.txt
export OPENAI_API_KEY=sk-...          # or pass api_key= explicitly
export LLM_MODEL_NAME=gpt-4o-mini     # optional, see app/core/config.py
```

### Running tests

```bash
pytest tests/unit/infrastructure/llm -v
```

**21 tests**, all using a hand-written `FakeOpenAIClient` (mimics the
real SDK's `.chat.completions.create()` shape) — no network calls, no
API key needed to test. This is the same injectable-client pattern
used for `SentenceTransformerEmbedder` in Phase 2, for the same
reason: `api.openai.com` is not reachable from this build sandbox
(confirmed: `curl -I https://api.openai.com` returns
`x-deny-reason: host_not_allowed`), so real API calls can't be
exercised here. The adapter code is complete and correct — swap in a
real `openai.OpenAI()` client (the default when no `client=` is
passed) and it works unchanged in any environment with normal
internet access.

I verified this isn't just unit-test theater by running the **actual
full pipeline** — real DOCX bytes through `ResumeParser`, through the
real `ScoringEngine`, producing a real failing `Evidence` item, fed
into `OpenAIProvider.suggest_improvement()` (with the fake client) —
end to end. See the "full pipeline proof" note below if you want to
reproduce it.

---

## Phase 4: Application Layer ✅

Wires Phases 1-3 together into real, callable use cases, plus a DI
container that is the single composition root of the backend.

```
app/application/
├── dto.py                      # Recommendation, AnalysisResult (thin wrappers
│                                 over domain entities -- no duplicate models)
├── container.py                 # ApplicationContainer + build_container():
│                                 the ONLY module allowed to import concrete
│                                 infra classes and wire them to use cases
└── use_cases/
    ├── analyze_resume_use_case.py         # raw file bytes + JD text -> AnalysisResult
    ├── match_job_description_use_case.py  # already-parsed Resume+JD -> ScoreCard
    └── generate_recommendations_use_case.py  # ScoreCard -> Recommendation[]
```

### The fallback guarantee (the important design decision in this phase)

`GenerateRecommendationsUseCase` never lets an LLM failure block or
break the analysis. If no LLM provider is configured, if the LLM
raises `UngroundedResponseError` (Phase 3), or if it fails for any
operational reason (network error, rate limit, timeout) — the use
case catches it and falls back to a deterministic, template-built
message straight from the `Evidence` fields. The user always gets a
traceable recommendation; the LLM is a quality enhancement on top of
that guarantee, never a dependency of it. This is unit tested directly
(`test_llm_failure_falls_back_to_template_never_raises`).

### The composition root pattern

`ApplicationContainer` / `build_container()` is the *only* place in
the codebase that imports both a concrete domain service (like
`ScoringEngine`) and a concrete infrastructure adapter (like
`ResumeParser`) side by side. Every other module — including every
use case — depends only on interfaces. This means:

- Swapping the embedder model, the LLM provider, or even the scoring
  weights is a one-line change in `build_container()`'s call site, not
  a hunt through the codebase.
- `use_llm=False` builds a fully offline container (recommendations
  always use the template fallback) — useful for CI, cost control, or
  a "fast tier" product mode.
- Every dependency is override-able via keyword argument, which is
  what makes the container itself unit-testable with fakes.

### Running tests

```bash
pytest tests/unit/application -v
```

**19 tests**, all using fakes for the parsers/embedder/LLM — no file
I/O, no network. Combined with Phases 1-3: **130 tests, 96% coverage,
0 regressions.**

I proved this phase works as a real system, not just as isolated
units: built a container with fakes standing in only for the two
network-bound adapters (embedder, LLM — same sandbox constraint as
Phases 2-3), then made **one call** —
`container.analyze_resume_use_case.execute(resume_bytes, filename,
jd_text)` — and got back a complete `AnalysisResult` with a real
score and real recommendations. This is the exact call Phase 6's API
endpoint will make.

---

## Phase 5: Persistence ✅

Real PostgreSQL persistence + Redis caching, tested against **real
running instances**, not mocks — this is the first phase where the
external dependency (a local database) isn't network-restricted, so
there's no reason to fake it.

```
app/domain/ports/
├── repository.py        # IResumeRepository, IJobDescriptionRepository
│                          (+ ResumeRecord/JobDescriptionRecord — thin
│                          metadata wrappers; Phase 1 entities stay pure)
└── cache.py              # ICache (generic get/set/delete)

app/application/ports.py  # IAnalysisRepository (lives here, not domain --
                            see its docstring for why)

app/infrastructure/persistence/
├── database.py            # engine/session factory (sync SQLAlchemy)
├── models.py               # ORM models: users, resumes, job_descriptions, analyses
├── mappers.py               # hand-written domain entity <-> JSON dict conversion
├── resume_repository.py     # SQLAlchemyResumeRepository
├── job_description_repository.py
├── analysis_repository.py
└── redis_cache.py           # RedisCache(ICache)

app/infrastructure/nlp/cached_embedder.py  # CachedEmbedder(IEmbedder) decorator

alembic/                    # migrations; one initial revision creates all 4 tables
```

### Key design decisions

- **JSONB, not full normalization.** Parsed resume/JD content and
  scorecard/evidence are stored as Postgres JSONB columns rather than
  exploded across dozens of tables (one per Skill, ExperienceEntry,
  Evidence, ...). The domain layer's dataclasses are the canonical
  shape; normalizing would mean hand-syncing two schemas. Revisitable
  via GIN-indexed JSONB queries if cross-resume SQL analytics become a
  real requirement — documented in `models.py`.
- **Hand-written mappers, not generic serialization.** `mappers.py`
  explicitly names every field on both encode and decode. A generic
  `dataclasses.asdict()` + recursive reconstructor would be shorter
  but silently fragile around `Optional[date]` fields and enums —
  exactly the kind of bug that's easy to miss in review.
- **`IAnalysisRepository` lives in `app/application/ports.py`, not
  `app/domain/ports`.** Its payload derives from `AnalysisResult`, an
  application-layer DTO — domain must never depend on application.
  `AnalysisRecord` also deliberately stores `scorecard` +
  `recommendations` directly rather than wrapping a full
  `AnalysisResult` (an earlier draft tried to fake `resume`/
  `job_description` as `None` to fit the wrapper, which silently
  violated `AnalysisResult`'s type contract — caught and fixed before
  shipping; see the git-equivalent history in this build if you want
  the full story).
- **Sync SQLAlchemy, not async.** Phase 8's Celery workers are
  synchronous by default; one DB access pattern for both API and
  workers avoids maintaining two.
- **`CachedEmbedder`** wraps any `IEmbedder` with Redis-backed caching
  keyed by text hash — concrete motivation: the same JD gets matched
  against many resumes, and common resume bullet phrasing recurs
  across resumes, so caching by text avoids redundant model calls.

### Setup

```bash
pip install -r requirements.txt
# Postgres + Redis must be running; then:
alembic upgrade head
```

Environment variables (see `app/core/config.py`):
`DATABASE_URL`, `REDIS_URL`, `EMBEDDING_CACHE_TTL_SECONDS`.

### Running tests

```bash
pytest tests/unit/infrastructure/persistence -v
```

**32 tests**, all running against a real local PostgreSQL test
database (`resume_scanner_test`) and a real local Redis instance (db
index 1, flushed before/after each test) — including a test that
proves the foreign-key constraint from `analyses` to `resumes`/
`job_descriptions` is real by asserting a save against nonexistent IDs
raises `IntegrityError`. Combined with Phases 1-4: **162 tests, 95%
coverage, 0 regressions.**

### A note on how this phase was actually verified

I didn't stop at unit/integration tests. I ran the complete chain for
real: built a container (fakes only for the two network-bound
adapters, same sandbox constraint as Phases 2-3) → parsed a real DOCX
→ scored it → **persisted the result to the real Postgres database** →
closed the session → opened a **fresh session** → **read it back** →
confirmed the score matched exactly. That fresh-session read-back is
the part that actually proves data survived a real round trip through
Postgres, not just that an ORM object stayed in memory.

---

## Phase 6: API (FastAPI + Auth + Celery) ✅

The system is now reachable over real HTTP — verified with a live
`uvicorn` server and real `curl` requests, not just `TestClient`.

```
app/api/
├── main.py                 # create_app() factory; builds ApplicationContainer
│                              once at startup (lifespan), registers routers/
│                              middleware/error handlers
├── dependencies.py          # get_db, get_container, get_current_user(_optional)
├── middleware.py            # request logging + X-Request-ID / X-Process-Time-Ms
├── errors.py                 # centralized exception -> {"error": {code, message}}
├── schemas/                  # typed Pydantic request/response models,
│                              built explicitly from domain entities (from_domain
│                              classmethods) -- not the JSONB storage shape
└── routers/
    ├── auth_router.py         # POST /register, /login (JWT), GET /me
    ├── resume_router.py       # POST /resumes (upload+parse), GET, list
    ├── job_description_router.py
    └── analysis_router.py     # POST /analyses/sync, /async, GET /tasks/{id}, GET /{id}

app/infrastructure/auth/security.py   # bcrypt hashing + JWT (python-jose)
app/infrastructure/persistence/user_repository.py  # deliberately NOT behind
                                        # a domain port -- see its docstring
app/infrastructure/tasks/
├── celery_app.py             # Celery instance, Redis broker+backend
└── analysis_tasks.py          # plain run_analysis() fn + thin Celery task wrapper
```

### Two analysis modes, same persistence

- **`POST /analyses/sync`** — runs in-process, returns the full result
  immediately. Simple; ties up a request worker for the duration.
- **`POST /analyses/async`** — enqueues a Celery task, returns a
  `task_id` immediately; poll `GET /analyses/tasks/{task_id}`. Use
  this under real load or for latency-sensitive endpoints.

Both call the exact same `AnalyzeResumeUseCase` (Phase 4) and persist
through the exact same repositories (Phase 5) — the only difference is
whether the work happens inline or on a worker.

### Bugs caught by actually running this, not just reading it

1. **`passlib` + `bcrypt` incompatibility.** `passlib` 1.7.4 doesn't
   understand `bcrypt`'s 4.x API change and raises
   `AttributeError: module 'bcrypt' has no attribute '__about__'` on
   the very first hash call. Caught immediately by testing password
   hashing before writing anything else — switched to `bcrypt`
   directly (`app/infrastructure/auth/security.py`).
2. **Repeated the Phase 5 `AnalysisResult(resume=None, ...)` mistake**
   while wiring `GET /analyses/{id}` — tried to fake required fields
   to reuse `AnalysisResponse.from_domain`. Caught in review before
   shipping; fixed by building the response schema directly from
   `AnalysisRecord.scorecard`/`.recommendations` instead.
3. **Celery eager-mode result storage.** `task_always_eager=True`
   alone doesn't store results in the backend (`AsyncResult` reads
   back `PENDING` even after the task actually succeeded) — needs
   `task_store_eager_result=True` too. Found by writing a test that
   actually polled the task status endpoint after completion, not by
   only checking the enqueue response.
4. **Background processes don't survive between sandbox tool calls.**
   PostgreSQL, Redis, and even a running `uvicorn` server were found
   dead on a subsequent command more than once during this build.
   Solved by starting services and running dependent commands in the
   same shell invocation — worth knowing if you hit "connection
   refused" errors reproducing this locally in a similarly ephemeral
   environment (a normal persistent server/VM will not have this
   issue).

### Setup

```bash
pip install -r requirements.txt
export JWT_SECRET_KEY="a-real-secret-not-the-dev-default"
uvicorn app.api.main:app --reload
# Optional, for async analysis:
celery -A app.infrastructure.tasks.celery_app worker --loglevel=info
```

Interactive API docs at `http://localhost:8000/docs` once running.

### Running tests

```bash
pytest tests/unit/api tests/unit/infrastructure/tasks -v
```

**29 tests**, running against the real test PostgreSQL database (via
FastAPI `dependency_overrides`, same test DB as Phase 5), real
password hashing, real JWT signing/verification, and Celery's eager
mode for the async path (no live worker/broker needed to test the
real task-dispatch code). Fakes are used only for the embedder/LLM,
same network constraint as every prior phase. Combined with Phases
1-5: **191 tests, 95% coverage, 0 regressions.**

### Proof: a real live server, not just TestClient

I started an actual `uvicorn` process and drove a complete workflow
against it with `curl` — register, login for a real JWT, upload a
real `.docx`, and receive back a real evidence-backed score over the
wire (82.1 overall, full per-criterion evidence, recommendations
correctly using the template fallback since no `OPENAI_API_KEY` was
set — exactly the Phase 4 guarantee, holding under real HTTP).

---

## Phase 9: Observability & Hardening ✅

Metrics, health checks, rate limiting, security headers, upload
limits, and a production fail-fast config check — all verified against
a real live server, not just unit tests.

```
app/api/
├── metrics.py               # Prometheus HTTP metrics + business metrics
│                              (analyses_total, analysis_duration_seconds,
│                              llm_fallback_total, category_score_percent)
├── health.py                  # liveness (/health) vs readiness (/health/ready,
│                                real DB+Redis pings)
├── rate_limit.py                # Redis-backed slowapi Limiter (see docs/SECURITY.md
│                                  for why Redis, not in-memory)
└── security_headers.py            # X-Content-Type-Options, X-Frame-Options,
                                      Referrer-Policy, Permissions-Policy, HSTS
```

Full detail in `docs/OBSERVABILITY.md`, `docs/SECURITY.md`, and
`docs/PERFORMANCE.md` (root of the repo) — including real measured
latency/throughput numbers and a captured live rate-limiting proof
(10 requests succeed, 11th–13th return real `429`s).

### A real bug caught here, worth knowing about if you write similar tests

`Settings` (Phase 1's config, frozen by design) can't be mutated with
`unittest.mock.patch.object(settings, "field", value)` — raises
`FrozenInstanceError`. The fix pattern used throughout the Phase 9
tests: `dataclasses.replace(settings, field=value)` to build a
modified copy, then `patch.object(module, "settings", modified_copy)`
on the **specific module's** already-imported `settings` name (not
`app.core.config.settings` — `from x import y` binds a local reference
at import time, so patching the origin module's attribute after the
fact doesn't affect an already-imported name elsewhere).

A second, subtler bug from the same test-writing session: a test
helper defined a FastAPI route inside a function that had
`from __future__ import annotations` active at module level, with
`Request` imported *locally* inside that same helper rather than at
module level. PEP 563 (postponed evaluation of annotations) turns
`request: Request` into the string `"Request"`, which FastAPI resolves
against the function's *module-level* globals via
`typing.get_type_hints()` — since `Request` wasn't there, every
request to that test route failed with a `422` (FastAPI treating
`request` as an unresolvable parameter) instead of correctly injecting
the `Request` object. Fixed by moving the import to module level. Both
bugs are exactly the kind that only surface when tests are actually
run, not when code is read — which is why every phase of this build
insisted on running things for real.

### Setup

```bash
pip install -r requirements.txt
export ENVIRONMENT=production   # optional; makes a default JWT secret a hard failure
export CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com
```

### Running tests

```bash
pytest tests/unit/api/test_rate_limiting.py tests/unit/api/test_security_headers.py \
       tests/unit/api/test_health.py tests/unit/api/test_metrics.py \
       tests/unit/api/test_upload_limits.py tests/unit/api/test_startup_config.py -v
```

**17 tests.** Combined with Phases 1–8: **208 tests, 95% coverage, 0
regressions.**

---

## Domain Layer (Phase 1, for reference)

This is the domain layer — pure Python, zero framework dependencies,
fully unit-tested. Everything in Phase 2+ depends on it, never the
other way around.

### Why this layer exists first

Every other part of the system — the API, the database, the parsers,
the embeddings, the LLM — is a *detail*. The thing that must never
depend on any of those details is the answer to "how do we turn a
resume and a job description into a trustworthy, explainable score?"
That logic lives here, and it's tested here, without spinning up a
database, a model server, or an HTTP client.

### The one rule that shapes everything here

**No score exists without an `Evidence[]` that produced it.**

This isn't a convention developers are asked to remember — it's
enforced structurally:

- Every `ICategoryScorer.score()` implementation ends by calling the
  shared `aggregate_evidence(category, evidence_list)` helper in
  `base.py`. That function computes `raw_score` as
  `(weight of passed evidence) / (total weight)` — there is no other
  code path to set a `CategoryScore.raw_score`.
- `ILLMProvider` (the port the Phase 3 OpenAI adapter implements) only
  exposes `explain_evidence(...)` and `suggest_improvement(...)`, both
  of which *require* an `Evidence`/`Evidence[]` argument. There is no
  method on that interface that lets an LLM originate a number.
- `IEmbedder.similarity()` results are never returned directly to a
  caller — `MatchingPolicy` always wraps them in an `Evidence` with
  the matched source text attached.

## What's Next

All 9 originally scoped phases are complete. Natural follow-ups beyond
the original roadmap, honestly listed rather than pretended-done:
refresh token rotation, email verification, per-account (not just
per-IP) failed-login tracking, CI-gated dependency vulnerability
scanning, and a codegen step to keep the frontend's hand-maintained
TypeScript types in sync with the backend's Pydantic schemas
automatically. See `docs/SECURITY.md`'s "What's explicitly NOT done
here" for the full, honest list.

## Running Everything Locally

```bash
# 1. Postgres + Redis (this repo was built/tested against local instances)
service postgresql start
redis-server --daemonize yes

# 2. Create the app database/user once:
psql -c "CREATE USER resume_scanner WITH PASSWORD 'resume_scanner_dev' CREATEDB;"
psql -c "CREATE DATABASE resume_scanner_dev OWNER resume_scanner;"

# 3. Install deps + run migrations
pip install -r requirements.txt
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.7.1/en_core_web_sm-3.7.1-py3-none-any.whl
alembic upgrade head

# 4. Run the API
export JWT_SECRET_KEY="change-me"
uvicorn app.api.main:app --reload

# 5. (Optional) Run a Celery worker for async analysis
celery -A app.infrastructure.tasks.celery_app worker --loglevel=info

# 6. Run the full test suite
pip install -r requirements-dev.txt
pytest tests/ -v --cov=app --cov-report=term-missing
```

