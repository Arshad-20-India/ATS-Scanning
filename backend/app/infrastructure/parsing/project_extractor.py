"""
Parses the "Projects" section body text into ProjectEntry objects.

Convention: first non-bullet line of a block is the project name
(optionally followed by a "Technologies: x, y, z" line). Bullet lines
are split into plain description bullets vs. "outcome" bullets (those
containing a digit/percentage/metric), matching how MatchingPolicy and
ProjectsScorer expect to consume this data.
"""

from __future__ import annotations

import re
from typing import List

from app.domain.entities.resume import ProjectEntry

_BULLET_PREFIX = re.compile(r"^[•\-*\u2022]\s*")
_TECH_LINE_PATTERN = re.compile(r"^technolog(?:y|ies)\s*:\s*(.+)$", re.IGNORECASE)
_NUMBER_PATTERN = re.compile(r"\d")


def extract_projects(section_text: str) -> List[ProjectEntry]:
    if not section_text.strip():
        return []

    blocks = re.split(r"\n\s*\n", section_text.strip())
    entries: List[ProjectEntry] = []

    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if not lines:
            continue

        name = lines[0]
        technologies: List[str] = []
        description_lines: List[str] = []
        outcomes: List[str] = []

        for line in lines[1:]:
            tech_match = _TECH_LINE_PATTERN.match(line)
            if tech_match:
                technologies = [
                    t.strip() for t in tech_match.group(1).split(",") if t.strip()
                ]
                continue

            cleaned = _BULLET_PREFIX.sub("", line).strip()
            if _NUMBER_PATTERN.search(cleaned):
                outcomes.append(cleaned)
            else:
                description_lines.append(cleaned)

        entries.append(
            ProjectEntry(
                name=name,
                description=" ".join(description_lines),
                technologies=technologies,
                outcomes=outcomes,
            )
        )

    return entries
