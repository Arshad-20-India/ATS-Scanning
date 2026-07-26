"""
GenerateRecommendationsUseCase: turns a ScoreCard's failing Evidence
into human-readable Recommendation objects.

Fallback strategy is the important design decision here: if no LLM
provider is configured, or the LLM raises UngroundedResponseError, or
the LLM call fails for any operational reason (network error, rate
limit, timeout), this use case NEVER returns nothing and never blocks
the analysis on the LLM being available. It falls back to a
deterministic, template-based message built directly from the
Evidence fields. This is the same principle as Phase 1/3 applied one
level up: the user always gets a traceable, evidence-grounded
recommendation, whether or not the LLM cooperated.
"""

from __future__ import annotations

import logging
from typing import List, Optional

from app.application.dto import Recommendation
from app.domain.entities.evidence import Evidence
from app.domain.entities.score import ScoreCard, ScoreCategory
from app.domain.ports.llm_provider import ILLMProvider

logger = logging.getLogger(__name__)

DEFAULT_MAX_RECOMMENDATIONS = 5


class GenerateRecommendationsUseCase:
    def __init__(
        self,
        llm_provider: Optional[ILLMProvider] = None,
        max_recommendations: int = DEFAULT_MAX_RECOMMENDATIONS,
    ) -> None:
        self._llm_provider = llm_provider
        self._max_recommendations = max_recommendations

    def execute(self, scorecard: ScoreCard) -> List[Recommendation]:
        prioritized = self._prioritize_failing_evidence(scorecard)

        recommendations = []
        for evidence, category in prioritized:
            message, is_llm_generated = self._build_message(evidence)
            recommendations.append(
                Recommendation(
                    criterion=evidence.criterion,
                    category=category,
                    message=message,
                    is_llm_generated=is_llm_generated,
                )
            )
        return recommendations

    def _prioritize_failing_evidence(
        self, scorecard: ScoreCard
    ) -> List[tuple[Evidence, ScoreCategory]]:
        """
        Highest-weight failing evidence first (the checks that matter
        most to the overall score), capped at max_recommendations so
        the user isn't overwhelmed with every minor gap at once.
        """
        pairs: List[tuple[Evidence, ScoreCategory]] = []
        for category, category_score in scorecard.category_scores.items():
            for evidence in category_score.failed_evidence:
                pairs.append((evidence, category))

        pairs.sort(key=lambda pair: pair[0].weight, reverse=True)
        return pairs[: self._max_recommendations]

    def _build_message(self, evidence: Evidence) -> tuple[str, bool]:
        if self._llm_provider is not None:
            try:
                message = self._llm_provider.suggest_improvement(
                    evidence, resume_context=evidence.source_span
                )
                return message, True
            except Exception:  # noqa: BLE001 -- any LLM failure falls back, never propagates
                logger.warning(
                    "LLM recommendation generation failed for criterion '%s'; "
                    "falling back to template.",
                    evidence.criterion,
                    exc_info=True,
                )

        return self._template_fallback(evidence), False

    @staticmethod
    def _template_fallback(evidence: Evidence) -> str:
        return (
            f"{evidence.description}. Expected: {evidence.expected_value!r}, "
            f"found: {evidence.found_value!r}."
        )
