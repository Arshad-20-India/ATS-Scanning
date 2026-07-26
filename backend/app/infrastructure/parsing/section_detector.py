"""
Deterministic section detection: finds header lines (e.g. "EXPERIENCE",
"Work Experience", "Skills") and splits the raw text into a dict of
{canonical_section_name: body_text}.

A "header line" is identified structurally, not just by keyword match:
it must be short (few words), contain no sentence-ending punctuation,
and match one of the known section-name patterns. This avoids
false-positives like a bullet that happens to mention "my experience
with Python" being mistaken for a section header.
"""

from __future__ import annotations

import re
from typing import Dict, List, Optional, Tuple

# canonical_name -> patterns that count as a header for that section
_SECTION_PATTERNS: Dict[str, List[str]] = {
    "summary": [
        r"^(professional\s+|executive\s+|career\s+)?summary$",
        r"^objective$",
        r"^profile$",
        r"^about\s+me$",
    ],
    "experience": [
        r"^(professional\s+|work\s+|employment\s+|career\s+|relevant\s+)?experience(s)?$",
        r"^work\s+history$",
        r"^employment\s+history$",
        r"^career\s+history$",
        r"^professional\s+background$",
    ],
    "education": [
        r"^education(al\s+background)?$",
        r"^academic\s+(background|qualifications|credentials)$",
        r"^education\s+(&|and)\s+(training|credentials)$",
        r"^degrees?$",
    ],
    "skills": [
        r"^(technical\s+|core\s+|key\s+|primary\s+)?skill(s)?$",
        r"^(technical\s+)?proficiencies$",
        r"^competencies$",
        r"^core\s+competencies$",
        r"^areas\s+of\s+expertise$",
        r"^skills?\s+(&|and)\s+(technologies|tools|frameworks)$",
        r"^technical\s+expertise$",
        r"^technology\s+stack$",
        r"^tech\s+stack$",
        r"^tool(s)?\s+(&|and)\s+technologies$",
        r"^skillset$",
    ],
    "projects": [
        r"^(key\s+|personal\s+|portfolio\s+|selected\s+)?projects?$",
        r"^projects?\s+(&|and)\s+initiatives$",
    ],
    "certifications": [
        r"^certifications?$",
        r"^licenses?\s+(&|and)\s+certifications?$",
        r"^certifications?\s+(&|and)\s+licenses?$",
        r"^credentials$",
    ],
}

_MAX_HEADER_WORDS = 5
_SENTENCE_PUNCTUATION = (".", ",", ";")


def _is_header_line(line: str, patterns: Dict[str, List[str]]) -> Optional[str]:
    stripped = line.strip()
    if not stripped or len(stripped.split()) > _MAX_HEADER_WORDS:
        return None
    if any(stripped.endswith(p) for p in _SENTENCE_PUNCTUATION):
        return None

    normalized = stripped.lower().rstrip(":").strip()
    for section_name, section_patterns in patterns.items():
        for pattern in section_patterns:
            if re.match(pattern, normalized):
                return section_name
    return None


def detect_sections(
    raw_text: str, patterns: Optional[Dict[str, List[str]]] = None
) -> Dict[str, str]:
    """
    Split raw_text into {section_name: body_text} using header-line
    detection. Pass a custom `patterns` dict to reuse this for
    non-resume documents (e.g. job descriptions) with different
    section vocabulary; defaults to resume section patterns.
    """
    active_patterns = patterns or _SECTION_PATTERNS
    lines = raw_text.splitlines()
    headers_found: List[Tuple[int, str]] = []

    for idx, line in enumerate(lines):
        section_name = _is_header_line(line, active_patterns)
        if section_name:
            headers_found.append((idx, section_name))

    if not headers_found:
        return {}

    sections: Dict[str, str] = {}
    for i, (start_idx, section_name) in enumerate(headers_found):
        end_idx = (
            headers_found[i + 1][0] if i + 1 < len(headers_found) else len(lines)
        )
        body = "\n".join(lines[start_idx + 1 : end_idx]).strip()
        # If the same section header appears twice, concatenate bodies
        # rather than overwrite -- avoids silently dropping content.
        if section_name in sections:
            sections[section_name] = sections[section_name] + "\n" + body
        else:
            sections[section_name] = body

    return sections
