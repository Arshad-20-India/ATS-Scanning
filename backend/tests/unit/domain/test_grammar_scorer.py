from __future__ import annotations

from dataclasses import replace

from app.domain.entities.job_description import JobDescription
from app.domain.entities.resume import GrammarFinding, WritingMetrics
from app.domain.services.category_scorers.grammar_scorer import GrammarScorer


def test_clean_writing_scores_well(sample_resume, sample_job_description):
    scorer = GrammarScorer()
    result = scorer.score(sample_resume, sample_job_description)
    assert result.raw_score == 1.0  # 1 minor warning, well within tolerance


def test_excessive_errors_fail_check(sample_resume, sample_job_description):
    many_errors = [
        GrammarFinding(rule_id=f"E{i}", message="err", severity="error", span="x")
        for i in range(5)
    ]
    resume = replace(sample_resume, grammar_findings=many_errors)
    scorer = GrammarScorer()
    result = scorer.score(resume, sample_job_description)

    error_evidence = next(e for e in result.evidence if e.criterion == "grammar_error_count")
    assert error_evidence.passed is False
    assert error_evidence.found_value == 5


def test_high_passive_voice_ratio_fails_check(sample_resume, sample_job_description):
    resume = replace(
        sample_resume,
        writing_metrics=WritingMetrics(passive_voice_ratio=0.5),
    )
    scorer = GrammarScorer()
    result = scorer.score(resume, sample_job_description)

    passive_evidence = next(e for e in result.evidence if e.criterion == "passive_voice_ratio")
    assert passive_evidence.passed is False
    assert passive_evidence.found_value == 0.5


def test_missing_writing_metrics_does_not_crash(sample_resume, sample_job_description):
    resume = replace(sample_resume, writing_metrics=None)
    scorer = GrammarScorer()
    result = scorer.score(resume, sample_job_description)
    assert result is not None
    assert not any(e.criterion == "passive_voice_ratio" for e in result.evidence)
