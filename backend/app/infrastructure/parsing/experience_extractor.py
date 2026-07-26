"""
Parses the "Experience" section body text into ExperienceEntry objects.

Heuristic (documented, not hidden): entries are separated by blank
lines. Two common header layouts are supported:

  1. Combined:  "Backend Engineer, Acme Corp | Jan 2021 - Jun 2023"
  2. Split:     "Backend Engineer, Acme Corp"
                "Jan 2021 - Jun 2023"

We detect layout (2) by checking whether a line parses as a date range
AND has essentially no other content (see
date_extractor.looks_like_date_only) -- if so, the *previous*
non-bullet line is treated as the title/company line. Otherwise we
fall back to layout (1), extracting the date range embedded in the
same line as the title/company text.

Lines starting with a bullet character become bullets; any other
non-header line is treated as a bullet too (better to over-capture as
a bullet than silently drop content).
"""

from __future__ import annotations

import re
from typing import List, Optional, Tuple

from app.domain.entities.resume import DateRange, ExperienceEntry
from app.infrastructure.parsing.date_extractor import (
    extract_date_range,
    looks_like_date_only,
)

_BULLET_PREFIX = re.compile(r"^[•\-*\u2022]\s*")
_SEPARATORS = re.compile(r"\s*(?:\||,|\u2013|-| at )\s*", re.IGNORECASE)


def extract_experience(section_text: str) -> List[ExperienceEntry]:
    if not section_text.strip():
        return []

    blocks = re.split(r"\n\s*\n", section_text.strip())
    entries: List[ExperienceEntry] = []

    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if not lines:
            continue

        header = _find_header(lines)
        if header is None:
            continue  # can't confidently parse this block; skip rather than guess

        title_idx, date_idx, date_range = header
        title_line = lines[title_idx] if title_idx is not None else None
        title, company = (
            _split_title_company(title_line) if title_line else ("Unknown", "Unknown")
        )

        excluded = {i for i in (title_idx, date_idx) if i is not None}
        bullets = [
            _BULLET_PREFIX.sub("", line).strip()
            for i, line in enumerate(lines)
            if i not in excluded
        ]

        entries.append(
            ExperienceEntry(
                title=title,
                company=company,
                date_range=date_range,
                bullets=[b for b in bullets if b],
            )
        )

    return entries


def _find_header(
    lines: List[str],
) -> Optional[Tuple[Optional[int], int, DateRange]]:
    # Layout 2: a dedicated date-only line, title on the preceding line.
    for idx, line in enumerate(lines):
        if _BULLET_PREFIX.match(line):
            continue
        if looks_like_date_only(line):
            date_range = extract_date_range(line)
            if date_range is None:
                continue
            title_idx = _previous_non_bullet_index(lines, idx)
            return title_idx, idx, date_range

    # Layout 1: title/company and date range combined on one line.
    for idx, line in enumerate(lines):
        if _BULLET_PREFIX.match(line):
            continue
        date_range = extract_date_range(line)
        if date_range is not None:
            return idx, idx, date_range

    return None


def _previous_non_bullet_index(lines: List[str], idx: int) -> Optional[int]:
    for i in range(idx - 1, -1, -1):
        if not _BULLET_PREFIX.match(lines[i]):
            return i
    return None


def _split_title_company(header_line: str) -> Tuple[str, str]:
    # Strip any embedded date-range text before splitting on
    # title/company separators (handles layout 1, where the date range
    # is embedded in the same line as the title/company).
    stripped = header_line
    for token in re.findall(r"[A-Za-z0-9/., ]{4,}", header_line):
        if extract_date_range(token) is not None:
            stripped = stripped.replace(token, "")

    parts = [p.strip() for p in _SEPARATORS.split(stripped) if p.strip()]
    if len(parts) >= 2:
        return parts[0], parts[1]
    if len(parts) == 1:
        return parts[0], "Unknown"
    return "Unknown", "Unknown"
