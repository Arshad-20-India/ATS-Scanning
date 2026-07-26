from __future__ import annotations

from app.domain.entities.evidence import Evidence
from app.domain.entities.job_description import JobDescription
from app.domain.entities.resume import Resume
from app.domain.entities.score import CategoryScore, ScoreCategory
from app.domain.services.category_scorers.base import ICategoryScorer, aggregate_evidence
from app.domain.services.skill_normalizer import SkillNormalizer

REQUIRED_SKILL_WEIGHT = 2.0
PREFERRED_SKILL_WEIGHT = 1.0


class SkillsScorer(ICategoryScorer):
    """
    Purely deterministic: a required/preferred skill either appears in
    the resume's normalized skill set or it doesn't. No embeddings
    here — see module docstring in skill_normalizer.py for why exact
    taxonomy matching is preferred over semantic similarity for this
    particular check.
    """

    category = ScoreCategory.SKILLS

    def __init__(self, normalizer: SkillNormalizer | None = None) -> None:
        self._normalizer = normalizer or SkillNormalizer()

    def score(self, resume: Resume, job_description: JobDescription) -> CategoryScore:
        resume_skills = {
            self._normalizer.normalize(skill.name) for skill in resume.skills
        }

        evidence = []
        for skill in job_description.required_skills:
            evidence.append(self._build_evidence(skill, resume_skills, required=True))
        for skill in job_description.preferred_skills:
            evidence.append(self._build_evidence(skill, resume_skills, required=False))

        return aggregate_evidence(self.category, evidence)

    def _build_evidence(
        self, skill: str, resume_skills: set[str], *, required: bool
    ) -> Evidence:
        normalized = self._normalizer.normalize(skill)
        found = normalized in resume_skills
        partial_match = None

        if not found:
            # Check if any candidate skill contains or is contained by the target skill
            for s in resume_skills:
                if normalized in s or s in normalized:
                    partial_match = s
                    break

        passed = found or (partial_match is not None)
        base_weight = REQUIRED_SKILL_WEIGHT if required else PREFERRED_SKILL_WEIGHT
        effective_weight = base_weight if found else (base_weight * 0.75 if partial_match else base_weight)

        if found:
            desc = f"{'Required' if required else 'Preferred'} skill '{skill}' verified in resume skills."
            source = "Verified Skill Match"
        elif partial_match:
            desc = f"{'Required' if required else 'Preferred'} skill '{skill}' matched via variant '{partial_match}' (Partial credit)."
            source = f"Variant: {partial_match}"
        else:
            desc = f"{'Required' if required else 'Preferred'} skill '{skill}' missing from resume."
            source = None

        return Evidence(
            criterion="required_skill_present" if required else "preferred_skill_present",
            description=desc,
            found_value=skill if found else (partial_match if partial_match else None),
            expected_value=skill,
            weight=effective_weight,
            passed=passed,
            confidence=1.0 if found else (0.85 if partial_match else 0.0),
            source_span=source,
        )
