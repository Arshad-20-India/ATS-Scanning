from __future__ import annotations

from app.infrastructure.parsing.education_extractor import extract_education


def test_extracts_degree_field_institution_and_year():
    text = "Bachelor of Science in Computer Science\nState University\n2020"
    entries = extract_education(text)
    assert len(entries) == 1
    entry = entries[0]
    assert "Bachelor" in entry.degree
    assert entry.field_of_study == "Computer Science"
    assert entry.institution == "State University"
    assert entry.graduation_date.year == 2020


def test_extracts_gpa_when_present():
    text = "Bachelor of Science in Computer Science\nState University\nGPA: 3.8"
    entries = extract_education(text)
    assert entries[0].gpa == 3.8


def test_no_degree_keyword_skips_block():
    text = "Some School\nDid a thing there\n2019"
    entries = extract_education(text)
    assert entries == []


def test_empty_section_returns_empty_list():
    assert extract_education("") == []
