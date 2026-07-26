"""
ScoringEngine is the single entry point the application layer calls to
turn (Resume, JobDescription) into a ScoreCard. It composes:

  - a list of ICategoryScorer implementations (which categories run,
    and with what internal thresholds — configurable per deployment)
  - a ScoringPolicy (how those category scores combine into one number)

Both are injected, not hardcoded, so:
  - a use case can run a subset of scorers (e.g. skip GrammarScorer
    for a "quick scan" endpoint)
  - the application composition root (not the domain layer) decides
    which scorers get a MatchingPolicy/embedder wired in

This class contains no I/O and no external dependencies whatsoever.
"""

from __future__ import annotations

from dataclasses import replace
from datetime import datetime, timezone
from typing import List

from app.domain.entities.job_description import JobDescription
from app.domain.entities.resume import Resume
from app.domain.entities.score import ScoreCard
from app.domain.services.category_scorers.base import ICategoryScorer
from app.domain.services.scoring_policy import ScoringPolicy


class ScoringEngine:
    def __init__(
        self, scorers: List[ICategoryScorer], policy: ScoringPolicy
    ) -> None:
        if not scorers:
            raise ValueError("ScoringEngine requires at least one category scorer")
        self._scorers = scorers
        self._policy = policy

    def evaluate(self, resume: Resume, job_description: JobDescription) -> ScoreCard:
        category_scores = {}

        for scorer in self._scorers:
            category_score = scorer.score(resume, job_description)
            weight = self._policy.weights.get(category_score.category, 0.0)
            category_scores[category_score.category] = replace(
                category_score, weight_in_overall=weight
            )

        overall_score = self._policy.compute_overall(category_scores)

        return ScoreCard(
            overall_score=overall_score,
            category_scores=category_scores,
            weights_used=self._policy.weights,
            generated_at=datetime.now(timezone.utc),
        )
