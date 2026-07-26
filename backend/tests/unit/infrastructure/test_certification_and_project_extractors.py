from __future__ import annotations

from app.infrastructure.parsing.certification_extractor import extract_certifications
from app.infrastructure.parsing.project_extractor import extract_projects


def test_certification_with_issuer_and_year():
    entries = extract_certifications("AWS Certified Developer - Amazon - 2022")
    assert len(entries) == 1
    assert entries[0].name == "AWS Certified Developer"
    assert entries[0].issuer == "Amazon"
    assert entries[0].date_earned.year == 2022


def test_certification_name_only():
    entries = extract_certifications("Certified Kubernetes Administrator")
    assert len(entries) == 1
    assert entries[0].name == "Certified Kubernetes Administrator"
    assert entries[0].issuer is None


def test_multiple_certification_lines():
    entries = extract_certifications("AWS Certified Developer\nPMP")
    assert len(entries) == 2


def test_project_with_technologies_and_outcomes():
    text = (
        "Open Source CLI Tool\n"
        "A CLI tool for automating deployments\n"
        "Technologies: Python, Docker\n"
        "- Adopted by 500 users\n"
        "- Simplified onboarding"
    )
    entries = extract_projects(text)
    assert len(entries) == 1
    project = entries[0]
    assert project.name == "Open Source CLI Tool"
    assert project.technologies == ["Python", "Docker"]
    assert "Adopted by 500 users" in project.outcomes
    assert "Simplified onboarding" in project.description


def test_empty_sections_return_empty_lists():
    assert extract_certifications("") == []
    assert extract_projects("") == []
