from __future__ import annotations

from dataclasses import replace

from app.domain.entities.job_description import JobDescription
from app.domain.services.category_scorers.ats_scorer import ATSScorer


def test_clean_resume_passes_all_ats_checks(sample_resume, sample_job_description):
    scorer = ATSScorer()
    result = scorer.score(sample_resume, sample_job_description)
    assert result.raw_score == 1.0
    assert all(e.passed for e in result.evidence)


def test_tables_flag_fails_check(sample_resume, sample_job_description):
    resume_with_tables = replace(
        sample_resume,
        formatting_flags=replace(sample_resume.formatting_flags, uses_tables=True),
    )
    scorer = ATSScorer()
    result = scorer.score(resume_with_tables, sample_job_description)

    tables_evidence = next(e for e in result.evidence if e.criterion == "no_tables_used")
    assert tables_evidence.passed is False
    assert result.raw_score < 1.0


def test_missing_section_flagged():
    from app.domain.entities.resume import ContactInfo, Resume

    resume = Resume(
        raw_text="",
        contact_info=ContactInfo(full_name="A", email="a@b.com"),
        sections_detected=["experience"],  # missing education, skills
    )
    jd = JobDescription(raw_text="", title="Eng")
    scorer = ATSScorer()
    result = scorer.score(resume, jd)

    sections_evidence = next(
        e for e in result.evidence if e.criterion == "required_sections_present"
    )
    assert sections_evidence.passed is False
    assert set(sections_evidence.found_value) == {"education", "skills"}


def test_incomplete_contact_info_flagged():
    from app.domain.entities.resume import ContactInfo, Resume

    resume = Resume(raw_text="", contact_info=ContactInfo(full_name="A"))  # no email/phone
    jd = JobDescription(raw_text="", title="Eng")
    scorer = ATSScorer()
    result = scorer.score(resume, jd)

    contact_evidence = next(
        e for e in result.evidence if e.criterion == "contact_info_extractable"
    )
    assert contact_evidence.passed is False
