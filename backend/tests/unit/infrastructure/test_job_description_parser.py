from __future__ import annotations

from app.infrastructure.parsing.job_description_parser import JobDescriptionParser


def test_parses_title(sample_jd_text):
    jd = JobDescriptionParser().parse(sample_jd_text)
    assert jd.title == "Backend Engineer"


def test_parses_required_and_preferred_skills(sample_jd_text):
    jd = JobDescriptionParser().parse(sample_jd_text)
    assert "Python" in jd.required_skills
    assert "JavaScript" in jd.required_skills
    assert "Kubernetes" in jd.preferred_skills
    assert "AWS" in jd.preferred_skills


def test_parses_min_years_experience(sample_jd_text):
    jd = JobDescriptionParser().parse(sample_jd_text)
    assert jd.min_years_experience == 3.0


def test_parses_required_education(sample_jd_text):
    jd = JobDescriptionParser().parse(sample_jd_text)
    assert jd.required_education is not None
    assert "bachelor" in jd.required_education.lower()


def test_builds_requirement_list_from_responsibilities_and_required(sample_jd_text):
    jd = JobDescriptionParser().parse(sample_jd_text)
    requirement_types = {r.requirement_type for r in jd.requirements}
    assert "experience" in requirement_types  # from Responsibilities
    assert "required_skill" in requirement_types
    assert "preferred_skill" in requirement_types


def test_no_matching_sections_falls_back_to_defaults():
    jd = JobDescriptionParser().parse("Just a plain paragraph with no structure.")
    assert jd.required_skills == []
    assert jd.min_years_experience is None
    assert jd.required_education is None


def test_years_and_education_lines_are_not_misclassified_as_skills():
    # Regression test: a JD's "Required" section commonly mixes skill
    # bullets with experience/education bullets under one header.
    text = (
        "Engineer\n\n"
        "Required\n"
        "- Python\n"
        "- 5+ years of experience\n"
        "- Bachelor's degree in Computer Science\n"
        "- Docker"
    )
    jd = JobDescriptionParser().parse(text)
    assert jd.required_skills == ["Python", "Docker"]
    assert jd.min_years_experience == 5.0
    assert jd.required_education == "Bachelor's"
    requirement_texts = [r.text for r in jd.requirements]
    assert "5+ years of experience" not in requirement_texts
