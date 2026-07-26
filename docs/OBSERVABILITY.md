# Observability

## Health checks

Two distinct endpoints, deliberately not one — see `app/api/health.py`
for the reasoning:

- **`GET /health`** — liveness. Zero dependencies, always returns
  `{"status": "ok"}` if the process can respond at all. An
  orchestrator should restart the container if this fails.
- **`GET /health/ready`** — readiness. Actually pings PostgreSQL
  (`SELECT 1`) and Redis (`PING`) with short timeouts. Returns `503`
  with `{"ready": false, "checks": {...}}` if either is down. A load
  balancer should stop routing new traffic here (without necessarily
  restarting the container) if this fails — useful during a database
  failover or Redis restart.

Both are wired into `backend/Dockerfile`'s `HEALTHCHECK` (liveness)
and can be pointed at by a Kubernetes readiness probe (readiness) if
deployed that way.

## Metrics

**`GET /metrics`** exposes Prometheus-format metrics (deliberately
excluded from the OpenAPI schema — it's an operational endpoint, not
part of the public API surface; verified by
`test_metrics_endpoint_not_in_openapi_schema`).

Two layers:

1. **Standard HTTP metrics** (via `prometheus-fastapi-instrumentator`):
   request counts, latency histograms, and in-progress requests,
   broken down by route and status code.
2. **Business metrics** (`app/api/metrics.py`), specific to what this
   platform actually promises:
   - `resume_scanner_analyses_total{mode="sync"|"async"}` — analysis
     volume by mode.
   - `resume_scanner_analysis_duration_seconds` — full pipeline
     latency (parse + score + persist), as a histogram.
   - `resume_scanner_category_score_percent{category="..."}` — score
     distribution per category, useful for noticing if e.g. the ATS
     compatibility check is failing unusually often across your real
     traffic (a signal worth investigating, not just per-user
     feedback).
   - **`resume_scanner_llm_fallback_total`** — the most important one.
     Phase 4's core design guarantee is that a recommendation is never
     blocked by an LLM failure (see
     `GenerateRecommendationsUseCase`'s docstring in
     `backend/README.md`). This counter makes that guarantee
     *observable*: if it's climbing fast in production, that's a
     signal your LLM provider is degraded, even though users are still
     getting a correct, evidence-backed response the whole time.

These are computed at the API layer (`record_analysis_metrics` in
`app/api/metrics.py`), reading only the already-returned
`AnalysisResult` — deliberately kept out of the application/domain
layers so `prometheus_client` never becomes a dependency of code that
has to stay testable and swappable (see the Clean Architecture
discussion in the root `README.md`).

## Logging

Structured-enough plaintext (`app/core/logging.py`): timestamp, level,
logger name, message. Every request gets logged with method, path,
status, duration, and a `X-Request-ID` (also returned as a response
header, so a client-reported issue can be correlated to a specific
server-side log line).

## Load testing

`scripts/load_test.py` + `scripts/benchmark_server.py` — see
`docs/PERFORMANCE.md` for actual measured results and how to reproduce
them yourself.
