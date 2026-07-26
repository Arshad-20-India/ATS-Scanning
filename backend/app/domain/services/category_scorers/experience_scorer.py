from __future__ import annotations

from datetime import date
from typing import List, Optional, Tuple

from app.domain.entities.evidence import Evidence
from app.domain.entities.job_description import JobDescription
from app.domain.entities.resume import ExperienceEntry, Resume
from app.domain.entities.score import CategoryScore, ScoreCategory
from app.domain.services.category_scorers.base import ICategoryScorer, aggregate_evidence
from app.domain.services.matching_policy import MatchingPolicy

YEARS_REQUIREMENT_WEIGHT = 3.0
GAP_WEIGHT = 0.5
MAX_ACCEPTABLE_GAP_MONTHS = 6


class ExperienceScorer(ICategoryScorer):
    """
    Combines three deterministic/semantic checks:
      1. Total years of experience vs. JD minimum (deterministic, from
         parsed date ranges).
      2. Employment gap detection (deterministic).
      3. Semantic relevance of experience bullets to JD "experience"
         requirements (delegated to MatchingPolicy, optional — the
         scorer works without it, just with fewer evidence items).
    """

    category = ScoreCategory.EXPERIENCE

    def __init__(self, matching_policy: Optional[MatchingPolicy] = None) -> None:
        self._matching_policy = matching_policy

    def score(self, resume: Resume, job_description: JobDescription) -> CategoryScore:
        evidence: List[Evidence] = []

        if job_description.min_years_experience is not None:
            evidence.append(self._years_evidence(resume, job_description))

        evidence.extend(self._gap_evidence(resume.experience))
        evidence.append(self._impact_density_evidence(resume.experience))

        if self._matching_policy is not None:
            exp_requirements = [
                r for r in job_description.requirements
                if r.requirement_type == "experience"
            ]
            for requirement in exp_requirements:
                evidence.append(
                    self._matching_policy.match_requirement_to_resume(
                        requirement, resume
                    )
                )

        return aggregate_evidence(self.category, evidence)

    @staticmethod
    def _impact_density_evidence(experience: List[ExperienceEntry]) -> Evidence:
        import re
        total_bullets = 0
        quantified_bullets = 0
        sample_metric_span = None

        metric_pattern = re.compile(r"(\d+(?:\.\d+)?%|\$\d+(?:\.\d+)?[kMB]?|\b\d+\+?\b)")

        for exp in experience:
            for bullet in exp.bullets:
                total_bullets += 1
                match = metric_pattern.search(bullet)
                if match:
                    quantified_bullets += 1
                    if not sample_metric_span:
                        sample_metric_span = f"'{match.group(0)}' in '{bullet[:60]}...'"

        if total_bullets == 0:
            return Evidence(
                criterion="quantified_metrics_density",
                description="Quantified Impact Density: No experience bullets found to measure.",
                found_value="0%",
                expected_value=">= 50%",
                weight=1.5,
                passed=False,
                confidence=1.0,
                source_span=None,
            )

        ratio = quantified_bullets / total_bullets
        percent_str = f"{round(ratio * 100)}%"
        passed = ratio >= 0.40  # 40%+ quantified bullets is baseline target

        return Evidence(
            criterion="quantified_metrics_density",
            description=(
                f"Quantified Impact Density: {quantified_bullets} of {total_bullets} bullet points ({percent_str}) "
                f"contain measurable metrics (%/$/numbers)."
            ),
            found_value=f"{quantified_bullets}/{total_bullets} bullets ({percent_str})",
            expected_value=">= 40% quantified bullets",
            weight=2.0,
            passed=passed,
            confidence=1.0,
            source_span=sample_metric_span or "Work experience section",
        )

    @staticmethod
    def _years_evidence(resume: Resume, job_description: JobDescription) -> Evidence:
        found_years = resume.total_experience_years
        required_years = job_description.min_years_experience
        passed = found_years >= required_years
        return Evidence(
            criterion="years_required_vs_found",
            description="Total years of professional experience",
            found_value=found_years,
            expected_value=required_years,
            weight=YEARS_REQUIREMENT_WEIGHT,
            passed=passed,
            confidence=1.0,
        )

    @staticmethod
    def _gap_evidence(experience: List[ExperienceEntry]) -> List[Evidence]:
        gaps = ExperienceScorer._detect_gaps(experience)
        evidence = []
        for gap_months, gap_start, gap_end in gaps:
            passed = gap_months <= MAX_ACCEPTABLE_GAP_MONTHS
            evidence.append(
                Evidence(
                    criterion="employment_gap",
                    description=(
                        f"Employment gap of {gap_months} month(s) detected "
                        f"between {gap_start.isoformat()} and {gap_end.isoformat()}"
                    ),
                    found_value=gap_months,
                    expected_value=f"<= {MAX_ACCEPTABLE_GAP_MONTHS} months",
                    weight=GAP_WEIGHT,
                    passed=passed,
                    confidence=1.0,
                )
            )
        return evidence

    @staticmethod
    def _detect_gaps(
        experience: List[ExperienceEntry],
    ) -> List[Tuple[int, date, date]]:
        if len(experience) < 2:
            return []

        sorted_entries = sorted(experience, key=lambda e: e.date_range.start)
        gaps: List[Tuple[int, date, date]] = []

        for previous, current in zip(sorted_entries, sorted_entries[1:]):
            previous_end = previous.date_range.end or date.today()
            gap_months = (
                (current.date_range.start.year - previous_end.year) * 12
                + (current.date_range.start.month - previous_end.month)
            )
            if gap_months > 1:
                gaps.append((gap_months, previous_end, current.date_range.start))

        return gaps
