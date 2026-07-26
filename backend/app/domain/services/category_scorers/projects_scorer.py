"""
ProjectsScorer: Evaluates project deliverables, technologies/tools used, and outcome metrics.
"""

from __future__ import annotations

from typing import List
from app.domain.entities.evidence import Evidence
from app.domain.entities.job_description import JobDescription
from app.domain.entities.resume import Resume, ProjectEntry
from app.domain.entities.score import CategoryScore, ScoreCategory
from app.domain.services.category_scorers.base import ICategoryScorer, aggregate_evidence


class ProjectsScorer(ICategoryScorer):
    category = ScoreCategory.PROJECTS

    def score(self, resume: Resume, job_description: JobDescription) -> CategoryScore:
        evidence: List[Evidence] = []
        projects = resume.projects

        # 1. Presence of Projects / Key Initiatives
        has_projects = len(projects) > 0 or ("project" in resume.raw_text.lower() or "initiative" in resume.raw_text.lower())
        evidence.append(
            Evidence(
                criterion="projects_present",
                description="Presence of documented Projects or Key Case Studies in candidate profile",
                found_value=f"{len(projects)} structured project(s)" if projects else ("Mentioned in text" if has_projects else "None found"),
                expected_value=">= 1 project/initiative",
                weight=1.5,
                passed=has_projects,
                confidence=1.0,
                source_span="Projects Section" if has_projects else None,
            )
        )

        # 2. Project Technology & Deliverable Alignment
        if projects:
            has_tech_tools = any(len(p.technologies) > 0 for p in projects)
            evidence.append(
                Evidence(
                    criterion="project_tools_utilization",
                    description="Clear documentation of tools, methodologies, or technologies applied in projects",
                    found_value="Tools/Methods documented" if has_tech_tools else "Basic description",
                    expected_value="Tools & Methods identified",
                    weight=1.0,
                    passed=has_tech_tools,
                    confidence=1.0,
                    source_span="Project Technologies",
                )
            )

        return aggregate_evidence(self.category, evidence)
