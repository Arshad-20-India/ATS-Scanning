"""
AnalyzeResumeUseCase: the primary end-to-end use case. Takes raw
resume file bytes and raw job description text and produces a
complete AnalysisResult (parsed entities + ScoreCard + recommendations).

This is pure orchestration -- parsing logic lives in the parsers,
scoring logic lives in ScoringEngine, recommendation logic lives in
GenerateRecommendationsUseCase. This class exists only to call them in
the right order and assemble the result, which is what keeps it small
and easy to verify by reading.
"""

from __future__ import annotations

from typing import Optional

from app.application.dto import AnalysisResult
from app.application.use_cases.generate_recommendations_use_case import (
    GenerateRecommendationsUseCase,
)
from app.domain.ports.parser import IJobDescriptionParser, IResumeParser
from app.domain.services.scoring_engine import ScoringEngine


class AnalyzeResumeUseCase:
    def __init__(
        self,
        resume_parser: IResumeParser,
        job_description_parser: IJobDescriptionParser,
        scoring_engine: ScoringEngine,
        recommendations_use_case: Optional[GenerateRecommendationsUseCase] = None,
    ) -> None:
        self._resume_parser = resume_parser
        self._job_description_parser = job_description_parser
        self._scoring_engine = scoring_engine
        self._recommendations_use_case = recommendations_use_case

    def execute(
        self,
        resume_file_bytes: bytes,
        filename: str,
        job_description_text: str,
        *,
        generate_recommendations: bool = True,
    ) -> AnalysisResult:
        resume = self._resume_parser.parse(resume_file_bytes, filename)
        job_description = self._job_description_parser.parse(job_description_text)
        scorecard = self._scoring_engine.evaluate(resume, job_description)

        recommendations = []
        if generate_recommendations and self._recommendations_use_case is not None:
            recommendations = self._recommendations_use_case.execute(scorecard)

        return AnalysisResult(
            resume=resume,
            job_description=job_description,
            scorecard=scorecard,
            recommendations=recommendations,
        )
