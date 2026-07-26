from __future__ import annotations

from app.infrastructure.parsing.skills_extractor import extract_skills


def test_splits_comma_separated_skills():
    skills = extract_skills("Python, JavaScript, Docker, Kubernetes")
    names = {s.name for s in skills}
    assert names == {"Python", "JavaScript", "Docker", "Kubernetes"}


def test_normalizes_and_dedupes_aliases():
    skills = extract_skills("Python, JS, JavaScript")
    normalized = {s.normalized_name for s in skills}
    assert normalized == {"python", "javascript"}
    assert len(skills) == 2  # JS and JavaScript collapse to one


def test_strips_category_label_prefix():
    skills = extract_skills("Languages: Python, Go\nTools: Docker")
    names = {s.name for s in skills}
    assert "Python" in names
    assert "Go" in names
    assert "Docker" in names


def test_empty_section_returns_empty_list():
    assert extract_skills("") == []
    assert extract_skills("   \n  ") == []
