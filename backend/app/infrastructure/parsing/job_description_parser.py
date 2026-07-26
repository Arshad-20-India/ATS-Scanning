"""
JobDescriptionParser: implements IJobDescriptionParser.

JD structure is less standardized than resumes, so extraction here is
intentionally conservative: we only populate a field when we found a
section/pattern we're confident about, and otherwise leave it at its
default (None / empty list) rather than guessing. A downstream scorer
(see EducationScorer, CertificationsScorer) already treats "no
requirement specified" as a full pass, so under-extraction is a safe
failure mode -- over-extraction (inventing a fake requirement) is not,
which is why we don't try to be clever here.
"""

from __future__ import annotations

import re
from typing import List, Optional

from app.domain.entities.job_description import JobDescription, JobRequirement
from app.infrastructure.parsing.section_detector import detect_sections

_JD_SECTION_PATTERNS = {
    "required": [
        r"^required$",
        r"^required\s+(skills|qualifications)$",
        r"^requirements$",
        r"^must\s+have$",
        r"^minimum\s+qualifications$",
    ],
    "preferred": [
        r"^preferred$",
        r"^preferred\s+(skills|qualifications)$",
        r"^nice\s+to\s+have$",
        r"^bonus\s+points?$",
    ],
    "responsibilities": [
        r"^responsibilities$",
        r"^what\s+you.ll\s+do$",
        r"^role$",
    ],
    "certifications": [r"^certifications?$", r"^required\s+certifications?$"],
}

_YEARS_PATTERN = re.compile(
    r"(\d+)\+?\s*-?\s*(?:to\s*(\d+))?\s*years?", re.IGNORECASE
)
_DEGREE_PATTERN = re.compile(
    r"\b(bachelor'?s?|master'?s?|phd|ph\.d\.?|associate'?s?|doctorate)\b",
    re.IGNORECASE,
)
_SPLIT_PATTERN = re.compile(r"[,\n|•*\u2022]+")
_BULLET_PREFIX = re.compile(r"^[•\-*\u2022]\s*")


class JobDescriptionParser:
    """Implements app.domain.ports.parser.IJobDescriptionParser."""

    def parse(self, text: str) -> JobDescription:
        sections = detect_sections(text, patterns=_JD_SECTION_PATTERNS)

        title = self._extract_title(text)
        required_skills = self._extract_skill_list(sections.get("required", ""))
        preferred_skills = self._extract_skill_list(sections.get("preferred", ""))
        min_years = self._extract_min_years(text)
        required_education = self._extract_education(text)
        required_certifications = self._extract_skill_list(
            sections.get("certifications", "")
        )
        requirements = self._build_requirements(sections)

        return JobDescription(
            raw_text=text,
            title=title,
            required_skills=required_skills,
            preferred_skills=preferred_skills,
            min_years_experience=min_years,
            required_education=required_education,
            required_certifications=required_certifications,
            requirements=requirements,
        )

    @staticmethod
    def _extract_title(text: str) -> str:
        for line in text.splitlines():
            stripped = line.strip()
            if stripped:
                return stripped[:120]
        return "Untitled Position"

    @staticmethod
    def _extract_skill_list(section_text: str) -> List[str]:
        if not section_text.strip():
            return []
        tokens = _SPLIT_PATTERN.split(section_text)
        cleaned = []
        for token in tokens:
            stripped = _BULLET_PREFIX.sub("", token).strip()
            if not stripped or len(stripped) > 60:
                continue
            # Lines that are actually years-of-experience or degree
            # requirements are captured separately (see
            # _extract_min_years / _extract_education) -- exclude them
            # here so they don't get misclassified as skill names.
            if _YEARS_PATTERN.search(stripped) or _DEGREE_PATTERN.search(stripped):
                continue
            cleaned.append(stripped)
        return cleaned

    @staticmethod
    def _extract_min_years(text: str) -> Optional[float]:
        match = _YEARS_PATTERN.search(text)
        if not match:
            return None
        return float(match.group(1))

    @staticmethod
    def _extract_education(text: str) -> Optional[str]:
        match = _DEGREE_PATTERN.search(text)
        if not match:
            return None
        raw = match.group(1)
        return raw[0].upper() + raw[1:].lower()

    @staticmethod
    def _build_requirements(sections: dict) -> List[JobRequirement]:
        requirements: List[JobRequirement] = []

        for line in _lines(sections.get("responsibilities", "")):
            requirements.append(
                JobRequirement(text=line, requirement_type="experience", weight=1.0)
            )
        for line in _lines(sections.get("required", "")):
            if _YEARS_PATTERN.search(line) or _DEGREE_PATTERN.search(line):
                continue
            requirements.append(
                JobRequirement(
                    text=line, requirement_type="required_skill", weight=2.0
                )
            )
        for line in _lines(sections.get("preferred", "")):
            if _YEARS_PATTERN.search(line) or _DEGREE_PATTERN.search(line):
                continue
            requirements.append(
                JobRequirement(
                    text=line, requirement_type="preferred_skill", weight=1.0
                )
            )

        return requirements


def _lines(section_text: str) -> List[str]:
    return [
        _BULLET_PREFIX.sub("", line).strip()
        for line in section_text.splitlines()
        if line.strip()
    ]
