"""
Skills extraction from the resume's "Skills" section text.

Splitting is deterministic: skills are typically separated by commas,
bullets, pipes, or newlines. We do not attempt to extract skills from
free-form prose elsewhere in the resume here -- that is a job for
semantic matching (MatchingPolicy) during scoring, not for building
the canonical skill list, to avoid polluting Resume.skills with
low-confidence guesses.
"""

from __future__ import annotations

import re
from typing import List

from app.domain.entities.resume import Skill
from app.domain.services.skill_normalizer import SkillNormalizer

_SPLIT_PATTERN = re.compile(r"[,\n|•*\u2022]+")


KNOWN_SKILLS_TAXONOMY = [
    "Python", "JavaScript", "TypeScript", "React", "Next.js", "Node.js", "Express", "FastAPI",
    "Django", "Flask", "PostgreSQL", "MySQL", "MongoDB", "Redis", "Docker", "Kubernetes",
    "AWS", "Amazon Web Services", "Azure", "GCP", "Google Cloud", "REST API", "GraphQL",
    "Git", "GitHub", "CI/CD", "Linux", "HTML", "CSS", "Tailwind", "Bootstrap", "Redux",
    "Jest", "C++", "C#", "Java", "Go", "Golang", "Rust", "PHP", "Laravel", "Spring Boot",
    "SEO", "SEO Strategy", "Google Analytics", "GA4", "Meta Ads", "Hubspot", "CRM", "A/B Testing",
    "Epic", "Epic EHR", "EHR", "BLS", "CPR", "HIPAA", "Triage", "Patient Care",
    "DCF", "DCF Valuation", "Financial Modeling", "PowerBI", "Tableau", "SQL", "Excel"
]


def extract_skills(
    skills_section_text: str,
    normalizer: SkillNormalizer | None = None,
    full_raw_text: str | None = None,
) -> List[Skill]:
    normalizer = normalizer or SkillNormalizer()

    target_text = skills_section_text.strip()
    source = "Skills"

    if not target_text and full_raw_text:
        target_text = full_raw_text
        source = "Full Resume Text"

    if not target_text:
        return []

    raw_tokens = _SPLIT_PATTERN.split(target_text)
    skills: List[Skill] = []
    seen: set[str] = set()

    for token in raw_tokens:
        cleaned = token.strip().strip("-").strip()
        cleaned = re.sub(r"^[A-Za-z ]+:\s*", "", cleaned)
        if not cleaned or len(cleaned) > 40:
            continue

        normalized = normalizer.normalize(cleaned)
        if normalized in seen:
            continue
        seen.add(normalized)

        skills.append(
            Skill(
                name=cleaned,
                normalized_name=normalized,
                source_section=source,
            )
        )

    # If section parsing produced no skills, scan full_raw_text for known taxonomy
    if not skills and full_raw_text:
        full_lower = full_raw_text.lower()
        for kw in KNOWN_SKILLS_TAXONOMY:
            if kw.lower() in full_lower:
                normalized = normalizer.normalize(kw)
                if normalized not in seen:
                    seen.add(normalized)
                    skills.append(
                        Skill(
                            name=kw,
                            normalized_name=normalized,
                            source_section="Full Text Keyword Scan",
                        )
                    )

    return skills
