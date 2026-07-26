from __future__ import annotations

from datetime import date

from app.infrastructure.parsing.date_extractor import (
    extract_date_range,
    looks_like_date_only,
)


def test_month_year_range():
    result = extract_date_range("Jan 2021 - Jun 2023")
    assert result.start == date(2021, 1, 1)
    assert result.end == date(2023, 6, 1)


def test_range_with_present():
    result = extract_date_range("Aug 2023 - Present")
    assert result.start == date(2023, 8, 1)
    assert result.end is None
    assert result.is_current is True


def test_range_with_en_dash():
    result = extract_date_range("2019 \u2013 2021")
    assert result.start == date(2019, 1, 1)
    assert result.end == date(2021, 1, 1)


def test_slash_month_format():
    result = extract_date_range("01/2021 - 06/2023")
    assert result.start == date(2021, 1, 1)
    assert result.end == date(2023, 6, 1)


def test_invalid_text_returns_none():
    assert extract_date_range("Backend Engineer") is None


def test_end_before_start_returns_none():
    assert extract_date_range("2023 - 2020") is None


def test_looks_like_date_only_true_cases():
    assert looks_like_date_only("Jan 2021 - Jun 2023") is True
    assert looks_like_date_only("2021 - Present") is True


def test_looks_like_date_only_false_when_other_text_present():
    assert looks_like_date_only("Backend Engineer, Acme Corp | Jan 2021 - Jun 2023") is False
    assert looks_like_date_only("Backend Engineer") is False
