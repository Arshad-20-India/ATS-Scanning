"""
Semantic matching between JD requirements and resume content.

This is the one place embeddings enter the scoring path. Note what
this class does NOT do: it never returns a bare float. It always wraps
the similarity result in an Evidence object with the matched source
text attached, so a UI can show the user exactly which resume bullet
was compared against which requirement and why it passed or failed the
threshold.

The IEmbedder dependency is injected (constructor injection), so this
class is fully unit-testable with a fake embedder that returns
hand-picked vectors — no real model load required in tests.
"""

from __future__ import annotations

from typing import List

from app.domain.entities.evidence import Evidence
from app.domain.entities.job_description import JobRequirement
from app.domain.entities.resume import Resume
from app.domain.ports.embedder import IEmbedder

DEFAULT_SIMILARITY_THRESHOLD = 0.55


class MatchingPolicy:
    def __init__(
        self,
        embedder: IEmbedder,
        similarity_threshold: float = DEFAULT_SIMILARITY_THRESHOLD,
    ) -> None:
        self._embedder = embedder
        self._threshold = similarity_threshold

    def match_requirement_to_resume(
        self, requirement: JobRequirement, resume: Resume
    ) -> Evidence:
        candidates = self._collect_candidate_texts(resume)

        if not candidates:
            return Evidence(
                criterion=f"semantic_match:{requirement.requirement_type}",
                description=(
                    f"Best semantic match in resume for requirement: "
                    f"'{requirement.text}'"
                ),
                found_value=None,
                expected_value=self._threshold,
                weight=requirement.weight,
                passed=False,
                confidence=0.0,
                source_span=None,
            )

        requirement_vector = self._embedder.embed([requirement.text])[0]
        candidate_vectors = self._embedder.embed(candidates)

        scored = [
            (text, self._embedder.similarity(requirement_vector, vec))
            for text, vec in zip(candidates, candidate_vectors)
        ]
        best_text, best_score = max(scored, key=lambda pair: pair[1])
        passed = best_score >= self._threshold

        return Evidence(
            criterion=f"semantic_match:{requirement.requirement_type}",
            description=(
                f"Best semantic match in resume for requirement: "
                f"'{requirement.text}'"
            ),
            found_value=round(best_score, 3),
            expected_value=self._threshold,
            weight=requirement.weight,
            passed=passed,
            confidence=round(best_score, 3),
            source_span=best_text,
        )

    @staticmethod
    def _collect_candidate_texts(resume: Resume) -> List[str]:
        texts: List[str] = []
        for exp in resume.experience:
            texts.extend(exp.bullets)
        for project in resume.projects:
            if project.description:
                texts.append(project.description)
            texts.extend(project.outcomes)
        return [t for t in texts if t and t.strip()]
