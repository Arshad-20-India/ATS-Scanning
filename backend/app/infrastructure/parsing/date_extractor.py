"""
Deterministic date-range parsing.

Resumes use a small, fairly predictable set of date formats. Rather
than reach for a heavyweight date-parsing library with unpredictable
fuzzy behavior, we match a fixed set of explicit patterns -- so every
successful parse is one we can vouch for, and failures are visible
(return None) rather than silently wrong.
"""

from __future__ import annotations

import re
from datetime import date
from typing import Optional

from app.domain.entities.resume import DateRange

_MONTHS = {
    "jan": 1, "january": 1, "feb": 2, "february": 2, "mar": 3, "march": 3,
    "apr": 4, "april": 4, "may": 5, "jun": 6, "june": 6, "jul": 7, "july": 7,
    "aug": 8, "august": 8, "sep": 9, "sept": 9, "september": 9, "oct": 10,
    "october": 10, "nov": 11, "november": 11, "dec": 12, "december": 12,
}
_MONTH_NAMES = "|".join(sorted(_MONTHS.keys(), key=len, reverse=True))

_CURRENT_KEYWORDS = {"present", "current", "now", "ongoing", "today"}

# "Jan 2021", "January 2021", "01/2021", "2021"
# NOTE: month/year separator is deliberately "/" only (not "-"), so a
# bare hyphen in the source text can always be treated unambiguously
# as a range separator (see _RANGE_SEPARATOR below) rather than
# colliding with a single date like "01-2021".
_SINGLE_DATE_PATTERN = re.compile(
    rf"(?:(?P<month_name>{_MONTH_NAMES})\.?\s+(?P<year1>\d{{4}}))"
    rf"|(?:(?P<month_num>\d{{1,2}})/(?P<year2>\d{{4}}))"
    rf"|(?:(?P<year3>\d{{4}}))",
    re.IGNORECASE,
)

_RANGE_SEPARATOR = re.compile(r"\s*(?:-|–|—|to)\s*", re.IGNORECASE)


def _parse_single_date(text: str) -> Optional[date]:
    text = text.strip()
    if text.lower() in _CURRENT_KEYWORDS:
        return None  # caller interprets None-as-current specially

    match = _SINGLE_DATE_PATTERN.search(text)
    if not match:
        return None

    if match.group("month_name"):
        month = _MONTHS[match.group("month_name").lower()]
        year = int(match.group("year1"))
        return date(year, month, 1)
    if match.group("month_num"):
        month = int(match.group("month_num"))
        year = int(match.group("year2"))
        if 1 <= month <= 12:
            return date(year, month, 1)
        return None
    if match.group("year3"):
        return date(int(match.group("year3")), 1, 1)

    return None


def extract_date_range(text: str) -> Optional[DateRange]:
    """
    Parse a date-range string like "Jan 2021 - Jun 2023" or
    "2021 - Present". Returns None if no confident parse is possible
    (never guesses).
    """
    parts = _RANGE_SEPARATOR.split(text.strip(), maxsplit=1)
    if len(parts) != 2:
        return None

    start_text, end_text = parts
    start_date = _parse_single_date(start_text)
    if start_date is None:
        return None

    if end_text.strip().lower() in _CURRENT_KEYWORDS:
        end_date = None
    else:
        end_date = _parse_single_date(end_text)
        if end_date is None:
            return None

    try:
        return DateRange(start=start_date, end=end_date)
    except ValueError:
        # end before start -- not a valid range, don't guess
        return None


_NON_DATE_TOKEN_PATTERN = re.compile(
    rf"({_MONTH_NAMES}|present|current|now|ongoing|today|\d+|[\s/\-–—,.()]|to)",
    re.IGNORECASE,
)


def looks_like_date_only(line: str) -> bool:
    """
    True if `line` parses as a date range AND essentially nothing else
    is on the line (used to tell apart a dedicated date-range line
    like "Jan 2021 - Jun 2023" from a combined line like
    "Backend Engineer, Acme Corp | Jan 2021 - Jun 2023").
    """
    stripped = line.strip()
    if not stripped or extract_date_range(stripped) is None:
        return False
    residual = _NON_DATE_TOKEN_PATTERN.sub("", stripped)
    return len(residual.strip()) == 0
