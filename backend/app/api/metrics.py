"""
Metrics.

Two layers:
1. Standard HTTP metrics (request count, latency histograms, in-
   progress requests) via prometheus-fastapi-instrumentator -- the
   generic "is the API healthy" signal any service needs.
2. Business metrics specific to what this platform actually promises.
   The most important one is `llm_fallback_total`: Phase 4's whole
   design is that a recommendation is never blocked by an LLM failure
   (see GenerateRecommendationsUseCase's docstring) -- this counter
   makes that guarantee *observable* in production. If it's climbing
   fast, that's a signal the LLM provider is degraded, even though
   users are still getting a correct response.
"""

from __future__ import annotations

from prometheus_client import Counter, Histogram
from prometheus_fastapi_instrumentator import Instrumentator

# --- Business metrics ---

analyses_total = Counter(
    "resume_scanner_analyses_total",
    "Total number of resume analyses run, by mode.",
    labelnames=["mode"],  # "sync" | "async"
)

analysis_duration_seconds = Histogram(
    "resume_scanner_analysis_duration_seconds",
    "Time to run a full resume analysis (parse + score + recommendations).",
    buckets=(0.5, 1, 2, 5, 10, 20, 30, 60),
)

llm_fallback_total = Counter(
    "resume_scanner_llm_fallback_total",
    "Times a recommendation fell back to the deterministic template "
    "because no LLM was configured, or the LLM call failed/was ungrounded.",
)

category_score_distribution = Histogram(
    "resume_scanner_category_score_percent",
    "Distribution of per-category scores produced by the scoring engine.",
    labelnames=["category"],
    buckets=(0, 20, 40, 60, 80, 100),
)


def instrument_app(app) -> None:
    """Wires up standard HTTP metrics + exposes /metrics. Call once at startup."""
    Instrumentator().instrument(app).expose(app, endpoint="/metrics", include_in_schema=False)


def record_analysis_metrics(result, mode: str, duration_seconds: float) -> None:
    """
    Records business metrics for one completed analysis. Takes the
    already-computed AnalysisResult (an application-layer DTO) rather
    than reaching into the use case internals -- keeps this a pure
    API/observability-layer concern, with zero metrics imports leaking
    into app/application or app/domain.
    """
    analyses_total.labels(mode=mode).inc()
    analysis_duration_seconds.observe(duration_seconds)

    for category_score in result.scorecard.category_scores.values():
        category_score_distribution.labels(category=category_score.category.value).observe(
            category_score.score_percent
        )

    fallback_count = sum(1 for r in result.recommendations if not r.is_llm_generated)
    if fallback_count:
        llm_fallback_total.inc(fallback_count)
