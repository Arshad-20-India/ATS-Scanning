"""
MatchJobDescriptionUseCase: scores an already-parsed Resume against an
already-parsed JobDescription.

Kept separate from AnalyzeResumeUseCase deliberately: re-scoring a
previously parsed and stored resume against a *new* job description
(a very common product flow -- "see how my resume matches this other
posting") shouldn't require re-parsing the original file or
re-generating recommendations unless requested. This use case does
exactly one thing: run the ScoringEngine.
"""

from __future__ import annotations

from app.domain.entities.job_description import JobDescription
from app.domain.entities.resume import Resume
from app.domain.entities.score import ScoreCard
from app.domain.services.scoring_engine import ScoringEngine


class MatchJobDescriptionUseCase:
    def __init__(self, scoring_engine: ScoringEngine) -> None:
        self._scoring_engine = scoring_engine

    def execute(self, resume: Resume, job_description: JobDescription) -> ScoreCard:
        return self._scoring_engine.evaluate(resume, job_description)
