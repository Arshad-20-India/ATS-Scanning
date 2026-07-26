from __future__ import annotations

from app.application.container import build_container
from app.domain.services.scoring_policy import ScoringPolicy


def test_use_llm_false_builds_container_with_no_llm_provider(
    fake_resume_parser, fake_jd_parser, fake_embedder
):
    container = build_container(
        resume_parser=fake_resume_parser,
        job_description_parser=fake_jd_parser,
        embedder=fake_embedder,
        use_llm=False,
    )
    assert container.llm_provider is None


def test_explicit_llm_provider_overrides_use_llm_flag(
    fake_resume_parser, fake_jd_parser, fake_embedder, fake_llm_provider
):
    container = build_container(
        resume_parser=fake_resume_parser,
        job_description_parser=fake_jd_parser,
        embedder=fake_embedder,
        llm_provider=fake_llm_provider,
        use_llm=False,  # should be irrelevant -- explicit provider wins
    )
    assert container.llm_provider is fake_llm_provider


def test_injected_dependencies_are_used_not_replaced(
    fake_resume_parser, fake_jd_parser, fake_embedder
):
    container = build_container(
        resume_parser=fake_resume_parser,
        job_description_parser=fake_jd_parser,
        embedder=fake_embedder,
        use_llm=False,
    )
    assert container.resume_parser is fake_resume_parser
    assert container.job_description_parser is fake_jd_parser
    assert container.embedder is fake_embedder


def test_container_wires_all_seven_scorers_into_scoring_engine(
    fake_resume_parser, fake_jd_parser, fake_embedder
):
    container = build_container(
        resume_parser=fake_resume_parser,
        job_description_parser=fake_jd_parser,
        embedder=fake_embedder,
        use_llm=False,
    )
    assert len(container.scoring_engine._scorers) == 7


def test_custom_scoring_policy_is_respected(
    fake_resume_parser, fake_jd_parser, fake_embedder
):
    from app.domain.entities.score import ScoreCategory

    custom_policy = ScoringPolicy(weights={ScoreCategory.SKILLS: 1.0})
    container = build_container(
        resume_parser=fake_resume_parser,
        job_description_parser=fake_jd_parser,
        embedder=fake_embedder,
        use_llm=False,
        scoring_policy=custom_policy,
    )
    assert container.scoring_engine._policy is custom_policy


def test_use_cases_are_wired_and_functional_end_to_end(
    fake_resume_parser, fake_jd_parser, fake_embedder, fake_llm_provider
):
    container = build_container(
        resume_parser=fake_resume_parser,
        job_description_parser=fake_jd_parser,
        embedder=fake_embedder,
        llm_provider=fake_llm_provider,
    )

    result = container.analyze_resume_use_case.execute(
        b"file-bytes", "resume.pdf", "jd text"
    )
    assert result.scorecard.overall_score >= 0.0

    scorecard_via_match = container.match_job_description_use_case.execute(
        result.resume, result.job_description
    )
    assert scorecard_via_match.overall_score == result.scorecard.overall_score
