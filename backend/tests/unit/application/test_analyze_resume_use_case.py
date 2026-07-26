from __future__ import annotations

from app.application.use_cases.analyze_resume_use_case import AnalyzeResumeUseCase
from app.application.use_cases.generate_recommendations_use_case import (
    GenerateRecommendationsUseCase,
)
from app.domain.services.category_scorers import SkillsScorer
from app.domain.services.scoring_engine import ScoringEngine
from app.domain.services.scoring_policy import ScoringPolicy


def _engine() -> ScoringEngine:
    return ScoringEngine(
        scorers=[SkillsScorer()],
        policy=ScoringPolicy(weights={SkillsScorer.category: 1.0}),
    )


def test_execute_calls_both_parsers_with_correct_arguments(
    fake_resume_parser, fake_jd_parser
):
    use_case = AnalyzeResumeUseCase(
        resume_parser=fake_resume_parser,
        job_description_parser=fake_jd_parser,
        scoring_engine=_engine(),
    )

    use_case.execute(b"file-bytes", "resume.pdf", "jd text")

    assert fake_resume_parser.parse_calls == [(b"file-bytes", "resume.pdf")]
    assert fake_jd_parser.parse_calls == ["jd text"]


def test_execute_produces_complete_analysis_result(fake_resume_parser, fake_jd_parser):
    use_case = AnalyzeResumeUseCase(
        resume_parser=fake_resume_parser,
        job_description_parser=fake_jd_parser,
        scoring_engine=_engine(),
    )

    result = use_case.execute(b"file-bytes", "resume.pdf", "jd text")

    assert result.resume.contact_info.full_name == "Jane Smith"
    assert result.job_description.title == "Backend Engineer"
    assert 0.0 <= result.scorecard.overall_score <= 100.0
    assert result.recommendations == []  # no recommendations_use_case configured


def test_recommendations_generated_when_use_case_configured(
    fake_resume_parser, fake_jd_parser, fake_llm_provider
):
    recommendations_use_case = GenerateRecommendationsUseCase(
        llm_provider=fake_llm_provider
    )
    use_case = AnalyzeResumeUseCase(
        resume_parser=fake_resume_parser,
        job_description_parser=fake_jd_parser,
        scoring_engine=_engine(),
        recommendations_use_case=recommendations_use_case,
    )

    result = use_case.execute(b"file-bytes", "resume.pdf", "jd text")

    # fixed_job_description requires Kubernetes, which fixed_resume lacks
    assert len(result.recommendations) >= 1


def test_generate_recommendations_flag_can_disable_recommendations(
    fake_resume_parser, fake_jd_parser, fake_llm_provider
):
    recommendations_use_case = GenerateRecommendationsUseCase(
        llm_provider=fake_llm_provider
    )
    use_case = AnalyzeResumeUseCase(
        resume_parser=fake_resume_parser,
        job_description_parser=fake_jd_parser,
        scoring_engine=_engine(),
        recommendations_use_case=recommendations_use_case,
    )

    result = use_case.execute(
        b"file-bytes", "resume.pdf", "jd text", generate_recommendations=False
    )

    assert result.recommendations == []
    assert fake_llm_provider.suggest_calls == 0
