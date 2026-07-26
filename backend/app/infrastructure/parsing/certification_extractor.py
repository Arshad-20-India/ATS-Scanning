"""
Parses the "Certifications" section body text into CertificationEntry
objects. Each non-empty line (or comma-separated token) is treated as
one certification, optionally with an issuer after a separator like
"-" or "|", and an optional year.
"""

from __future__ import annotations

import re
from typing import List, Optional

from app.domain.entities.resume import CertificationEntry

_YEAR_PATTERN = re.compile(r"\b(19|20)\d{2}\b")
_BULLET_PREFIX = re.compile(r"^[•\-*\u2022]\s*")
_SEPARATOR = re.compile(r"\s*[|\u2013]\s*|\s+-\s+")


def extract_certifications(section_text: str) -> List[CertificationEntry]:
    if not section_text.strip():
        return []

    entries: List[CertificationEntry] = []
    lines = [
        _BULLET_PREFIX.sub("", line).strip()
        for line in section_text.splitlines()
        if line.strip()
    ]

    for line in lines:
        year_match = _YEAR_PATTERN.search(line)
        date_earned = None
        if year_match:
            from datetime import date as date_cls
            date_earned = date_cls(int(year_match.group(0)), 1, 1)
            line = line.replace(year_match.group(0), "").strip(" ,()-")

        parts = [p.strip() for p in _SEPARATOR.split(line) if p.strip()]
        name = parts[0] if parts else line
        issuer = parts[1] if len(parts) > 1 else None

        if name:
            entries.append(
                CertificationEntry(name=name, issuer=issuer, date_earned=date_earned)
            )

    return entries
