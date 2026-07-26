from __future__ import annotations

from app.infrastructure.parsing.section_detector import detect_sections


def test_detects_standard_resume_sections(sample_resume_text):
    sections = detect_sections(sample_resume_text)
    assert set(sections.keys()) == {
        "summary", "experience", "education", "skills", "projects", "certifications",
    }
    assert "Backend Engineer" in sections["experience"]


def test_no_headers_returns_empty_dict():
    assert detect_sections("just some plain text with no headers at all") == {}


def test_bullet_mentioning_keyword_is_not_mistaken_for_header():
    text = "Experience\n- I have 5 years of experience with Python and skills in Docker."
    sections = detect_sections(text)
    assert "experience" in sections
    assert "skills" not in sections  # the bullet line must not be parsed as a header


def test_duplicate_headers_are_concatenated_not_overwritten():
    text = "Skills\nPython\n\nExperience\n- did stuff\n\nSkills\nDocker"
    sections = detect_sections(text)
    assert "Python" in sections["skills"]
    assert "Docker" in sections["skills"]
