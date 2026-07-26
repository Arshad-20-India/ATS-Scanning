from __future__ import annotations

from datetime import date

from app.infrastructure.parsing.experience_extractor import extract_experience


def test_split_layout_title_then_date_on_next_line():
    text = (
        "Backend Engineer, Acme Corp\n"
        "Jan 2021 - Jun 2023\n"
        "- Built a scalable REST API\n"
        "- Reduced latency by 40%"
    )
    entries = extract_experience(text)
    assert len(entries) == 1
    assert entries[0].title == "Backend Engineer"
    assert entries[0].company == "Acme Corp"
    assert entries[0].date_range.start == date(2021, 1, 1)
    assert entries[0].date_range.end == date(2023, 6, 1)
    assert len(entries[0].bullets) == 2


def test_combined_layout_title_and_date_same_line():
    text = (
        "Backend Engineer, Acme Corp | Jan 2021 - Jun 2023\n"
        "- Built a scalable REST API"
    )
    entries = extract_experience(text)
    assert len(entries) == 1
    assert entries[0].title == "Backend Engineer"
    assert entries[0].company == "Acme Corp"
    assert len(entries[0].bullets) == 1


def test_multiple_entries_separated_by_blank_line():
    text = (
        "Backend Engineer, Acme Corp\n"
        "Jan 2021 - Jun 2023\n"
        "- Bullet one\n"
        "\n"
        "Software Engineer, Beta Inc\n"
        "Aug 2023 - Present\n"
        "- Bullet two"
    )
    entries = extract_experience(text)
    assert len(entries) == 2
    assert entries[1].title == "Software Engineer"
    assert entries[1].date_range.is_current is True


def test_unparseable_block_is_skipped_not_guessed():
    text = "Just some prose with no date range or clear structure at all."
    entries = extract_experience(text)
    assert entries == []


def test_empty_section_returns_empty_list():
    assert extract_experience("") == []
