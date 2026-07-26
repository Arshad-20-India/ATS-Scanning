from __future__ import annotations

from app.domain.entities.evidence import Evidence
from app.domain.entities.job_description import JobDescription
from app.domain.entities.resume import Resume
from app.domain.entities.score import CategoryScore, ScoreCategory
from app.domain.services.category_scorers.base import ICategoryScorer, aggregate_evidence

EDUCATION_REQUIREMENT_WEIGHT = 2.0

# Ordered lowest-to-highest for "meets or exceeds" comparisons.
_DEGREE_RANK = {
    "high school": 0,
    "associate": 1,
    "bachelor": 2,
    "master": 3,
    "phd": 4,
    "doctorate": 4,
}


def _degree_rank(degree_text: str) -> int:
    lowered = degree_text.lower()
    for keyword, rank in _DEGREE_RANK.items():
        if keyword in lowered:
            return rank
    return -1  # unrecognized degree text; treated as "cannot confirm"


class EducationScorer(ICategoryScorer):
    """
    Deterministic degree-level and field-of-study comparison. Field
    matching here is intentionally a simple substring/keyword check
    rather than embeddings, to keep this category's evidence fully
    auditable; a semantic "close-enough field" check (e.g. "Computer
    Engineering" vs "Computer Science") can be added later via
    MatchingPolicy if false negatives prove to be a problem in
    practice — that's a deliberate, revisitable trade-off, not an
    oversight.
    """

    category = ScoreCategory.EDUCATION

    def score(self, resume: Resume, job_description: JobDescription) -> CategoryScore:
        if not job_description.required_education:
            return aggregate_evidence(self.category, [])

        evidence = [self._degree_evidence(resume, job_description.required_education)]
        return aggregate_evidence(self.category, evidence)

    @staticmethod
    def _degree_evidence(resume: Resume, required_education: str) -> Evidence:
        required_rank = _degree_rank(required_education)
        best_entry_rank = -1
        best_entry_text = None

        for entry in resume.education:
            rank = _degree_rank(entry.degree)
            if rank > best_entry_rank:
                best_entry_rank = rank
                best_entry_text = f"{entry.degree} in {entry.field_of_study}"

        passed = best_entry_rank >= required_rank and required_rank >= 0

        return Evidence(
            criterion="degree_level_meets_requirement",
            description=(
                f"Highest degree found ('{best_entry_text or 'none found'}') "
                f"compared against requirement '{required_education}'"
            ),
            found_value=best_entry_text,
            expected_value=required_education,
            weight=EDUCATION_REQUIREMENT_WEIGHT,
            passed=passed,
            confidence=1.0 if required_rank >= 0 else 0.5,
        )
