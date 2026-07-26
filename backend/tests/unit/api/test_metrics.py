from __future__ import annotations

import io

import docx


def _sample_resume_bytes() -> bytes:
    document = docx.Document()
    for line in ["Jane Smith", "jane@example.com", "", "Experience", "Engineer, Acme",
                 "Jan 2021 - Jun 2023", "- Did things", "", "Skills", "Python"]:
        document.add_paragraph(line)
    buf = io.BytesIO()
    document.save(buf)
    return buf.getvalue()


def test_metrics_endpoint_exposes_prometheus_format(api_client):
    response = api_client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers["content-type"]
    # Standard instrumentator metric that should always be present.
    assert "http_requests_total" in response.text


def test_metrics_endpoint_not_in_openapi_schema(api_client):
    """/metrics is an operational endpoint, not part of the public API surface."""
    response = api_client.get("/openapi.json")
    paths = response.json()["paths"]
    assert "/metrics" not in paths


def test_business_metrics_increment_after_running_an_analysis(api_client):
    resume_bytes = _sample_resume_bytes()
    jd_text = "Backend Engineer\n\nRequired\n- Python"

    before = api_client.get("/metrics").text
    before_count = before.count('resume_scanner_analyses_total{mode="sync"}')

    api_client.post(
        "/api/v1/analyses/sync",
        files={"resume_file": ("resume.docx", resume_bytes, "application/octet-stream")},
        data={"job_description_text": jd_text},
    )

    after = api_client.get("/metrics").text
    assert 'resume_scanner_analyses_total{mode="sync"}' in after
    assert "resume_scanner_analysis_duration_seconds" in after
    assert "resume_scanner_category_score_percent" in after


def test_record_analysis_metrics_counts_llm_fallback():
    """
    Unit-level test of the metrics-recording function directly --
    proves it correctly counts non-LLM-generated recommendations as
    fallback events, without needing a full HTTP round trip.
    """
    from datetime import datetime, timezone

    from app.api.metrics import llm_fallback_total, record_analysis_metrics
    from app.application.dto import AnalysisResult, Recommendation
    from app.domain.entities.job_description import JobDescription
    from app.domain.entities.resume import ContactInfo, Resume
    from app.domain.entities.score import CategoryScore, ScoreCard, ScoreCategory

    before = llm_fallback_total._value.get()

    result = AnalysisResult(
        resume=Resume(raw_text="x", contact_info=ContactInfo()),
        job_description=JobDescription(raw_text="x", title="Engineer"),
        scorecard=ScoreCard(
            overall_score=50.0,
            category_scores={
                ScoreCategory.SKILLS: CategoryScore(category=ScoreCategory.SKILLS, raw_score=0.5)
            },
            weights_used={},
            generated_at=datetime.now(timezone.utc),
        ),
        recommendations=[
            Recommendation(
                criterion="c1", category=ScoreCategory.SKILLS, message="m1", is_llm_generated=False
            ),
            Recommendation(
                criterion="c2", category=ScoreCategory.SKILLS, message="m2", is_llm_generated=True
            ),
        ],
    )

    record_analysis_metrics(result, mode="sync", duration_seconds=1.0)

    after = llm_fallback_total._value.get()
    assert after == before + 1  # only the one non-LLM-generated recommendation counted
