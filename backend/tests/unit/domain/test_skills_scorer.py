from __future__ import annotations

from app.domain.entities.job_description import JobDescription
from app.domain.services.category_scorers.skills_scorer import SkillsScorer


def test_all_required_and_preferred_skills_found(sample_resume, sample_job_description):
    scorer = SkillsScorer()
    result = scorer.score(sample_resume, sample_job_description)

    # required_skills=["Python", "JavaScript"] both present (JS aliases to javascript)
    # preferred_skills=["Kubernetes"] NOT present
    assert result.category.value == "skills"
    required_evidence = [e for e in result.evidence if e.criterion == "required_skill_present"]
    preferred_evidence = [e for e in result.evidence if e.criterion == "preferred_skill_present"]

    assert all(e.passed for e in required_evidence)
    assert len(required_evidence) == 2
    assert len(preferred_evidence) == 1
    assert preferred_evidence[0].passed is False

    # score = (2*2.0) / (2*2.0 + 1*1.0) = 4/5 = 0.8
    assert result.raw_score == 0.8


def test_alias_resolution_js_matches_javascript(sample_resume):
    jd = JobDescription(
        raw_text="",
        title="Engineer",
        required_skills=["JavaScript"],
    )
    scorer = SkillsScorer()
    result = scorer.score(sample_resume, jd)
    assert result.raw_score == 1.0
    assert result.evidence[0].passed is True


def test_missing_required_skill_fails_and_is_traceable(sample_resume):
    jd = JobDescription(raw_text="", title="Engineer", required_skills=["Rust"])
    scorer = SkillsScorer()
    result = scorer.score(sample_resume, jd)

    assert result.raw_score == 0.0
    assert result.evidence[0].passed is False
    assert result.evidence[0].found_value is False
    assert "Rust" in result.evidence[0].description


def test_no_required_or_preferred_skills_scores_perfect_with_explanation():
    jd = JobDescription(raw_text="", title="Engineer")
    scorer = SkillsScorer()

    from app.domain.entities.resume import ContactInfo, Resume

    empty_resume = Resume(raw_text="", contact_info=ContactInfo())
    result = scorer.score(empty_resume, jd)

    assert result.raw_score == 1.0
    assert result.evidence[0].criterion == "no_requirements_specified"
