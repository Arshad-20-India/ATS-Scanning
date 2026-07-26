"""
Parses the "Education" section body text into EducationEntry objects.
"""

from __future__ import annotations

import re
from typing import List, Optional

from app.domain.entities.resume import EducationEntry
from app.infrastructure.parsing.date_extractor import extract_date_range

_DEGREE_KEYWORDS = (
    "bachelor", "b.s.", "b.a.", "bs ", "ba ",
    "master", "m.s.", "m.a.", "ms ", "ma ", "mba",
    "phd", "ph.d.", "doctorate", "associate",
)

_GPA_PATTERN = re.compile(r"gpa[:\s]+([0-4]\.\d{1,2})", re.IGNORECASE)
_FIELD_PATTERN = re.compile(r"\bin\s+([A-Za-z][A-Za-z &,]+)", re.IGNORECASE)


def extract_education(section_text: str) -> List[EducationEntry]:
    if not section_text.strip():
        return []

    blocks = re.split(r"\n\s*\n", section_text.strip())
    entries: List[EducationEntry] = []

    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if not lines:
            continue

        degree_line = _find_degree_line(lines)
        if degree_line is None:
            continue

        degree = _extract_degree_phrase(degree_line)
        field = _extract_field(degree_line)
        institution = _guess_institution(lines, degree_line)
        graduation_date = _extract_graduation_date(lines)
        gpa = _extract_gpa(block)

        entries.append(
            EducationEntry(
                degree=degree,
                field_of_study=field,
                institution=institution,
                graduation_date=graduation_date,
                gpa=gpa,
            )
        )

    return entries


def _find_degree_line(lines: List[str]) -> Optional[str]:
    for line in lines:
        lowered = line.lower()
        if any(keyword in lowered for keyword in _DEGREE_KEYWORDS):
            return line
    return None


def _extract_degree_phrase(line: str) -> str:
    lowered = line.lower()
    for keyword in _DEGREE_KEYWORDS:
        if keyword in lowered:
            idx = lowered.index(keyword)
            # take a small window starting at the keyword up to "in"/comma
            remainder = line[idx:]
            cutoff = re.search(r"\bin\b|,", remainder, re.IGNORECASE)
            phrase = remainder[: cutoff.start()] if cutoff else remainder
            return phrase.strip().rstrip(",")
    return line.strip()


def _extract_field(line: str) -> str:
    match = _FIELD_PATTERN.search(line)
    if match:
        field = match.group(1).strip().rstrip(",")
        return field
    return "Unknown"


def _guess_institution(lines: List[str], degree_line: str) -> str:
    for line in lines:
        if line != degree_line and not extract_date_range(line):
            return line
    return "Unknown"


def _extract_graduation_date(lines: List[str]):
    for line in lines:
        date_range = extract_date_range(line)
        if date_range is not None:
            return date_range.end or date_range.start
        # Single graduation year like "2020" on its own line
        year_match = re.fullmatch(r"(19|20)\d{2}", line.strip())
        if year_match:
            from datetime import date as date_cls
            return date_cls(int(year_match.group(0)), 1, 1)
    return None


def _extract_gpa(block_text: str) -> Optional[float]:
    match = _GPA_PATTERN.search(block_text)
    return float(match.group(1)) if match else None
