"""
ApplicationContainer: the single composition root of the backend.

This is the *only* module in the entire codebase that is allowed to
import concrete infrastructure classes (ResumeParser, OpenAIProvider,
SentenceTransformerEmbedder, ...) AND concrete domain services
(ScoringEngine, category scorers) in the same place, and wire them
together. Every other module depends on interfaces/abstractions;
this one is where the abstractions get filled in with real
implementations.

Phase 6 (API layer) will build one ApplicationContainer at process
startup and inject its use cases into FastAPI route handlers via
dependency injection -- this module is what that DI wiring will point
to.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from app.application.use_cases.analyze_resume_use_case import AnalyzeResumeUseCase
from app.application.use_cases.generate_recommendations_use_case import (
    GenerateRecommendationsUseCase,
)
from app.application.use_cases.match_job_description_use_case import (
    MatchJobDescriptionUseCase,
)
from app.application.use_cases.rewrite_resume_use_case import RewriteResumeUseCase
from app.core.config import settings
from app.domain.ports.embedder import IEmbedder
from app.domain.ports.llm_provider import ILLMProvider
from app.domain.ports.parser import IJobDescriptionParser, IResumeParser
from app.domain.services.category_scorers import (
    ATSScorer,
    CertificationsScorer,
    EducationScorer,
    ExperienceScorer,
    GrammarScorer,
    ProjectsScorer,
    SkillsScorer,
    SemanticVectorScorer,
)
from app.domain.services.matching_policy import MatchingPolicy
from app.domain.services.scoring_engine import ScoringEngine
from app.domain.services.scoring_policy import ScoringPolicy
from app.infrastructure.llm.provider_factory import get_llm_provider
from app.infrastructure.nlp.sentence_transformer_embedder import (
    SentenceTransformerEmbedder,
)
from app.infrastructure.parsing.job_description_parser import JobDescriptionParser
from app.infrastructure.parsing.resume_parser import ResumeParser


@dataclass(frozen=True)
class ApplicationContainer:
    resume_parser: IResumeParser
    job_description_parser: IJobDescriptionParser
    embedder: IEmbedder
    llm_provider: Optional[ILLMProvider]
    scoring_engine: ScoringEngine
    analyze_resume_use_case: AnalyzeResumeUseCase
    match_job_description_use_case: MatchJobDescriptionUseCase
    generate_recommendations_use_case: GenerateRecommendationsUseCase
    rewrite_resume_use_case: RewriteResumeUseCase


def build_container(
    *,
    resume_parser: Optional[IResumeParser] = None,
    job_description_parser: Optional[IJobDescriptionParser] = None,
    embedder: Optional[IEmbedder] = None,
    llm_provider: Optional[ILLMProvider] = None,
    use_llm: bool = True,
    scoring_policy: Optional[ScoringPolicy] = None,
    similarity_threshold: Optional[float] = None,
) -> ApplicationContainer:
    """
    Build a fully-wired ApplicationContainer.

    Every dependency can be overridden -- this is what makes the
    container itself testable (inject fakes) as well as flexible in
    production (e.g. swap the embedder model via config without
    touching this function's callers).

    `use_llm=False` builds a container with no LLM provider at all
    (GenerateRecommendationsUseCase then always uses its template
    fallback) -- useful for offline/CI environments or a "fast, no-LLM
    tier" product mode. Passing an explicit `llm_provider=` always
    takes precedence over `use_llm`.
    """
    resolved_resume_parser = resume_parser or ResumeParser()
    resolved_jd_parser = job_description_parser or JobDescriptionParser()
    resolved_embedder = embedder or SentenceTransformerEmbedder()

    resolved_llm_provider = llm_provider
    if resolved_llm_provider is None and use_llm:
        resolved_llm_provider = get_llm_provider()

    threshold = (
        similarity_threshold
        if similarity_threshold is not None
        else settings.semantic_similarity_threshold
    )
    matching_policy = MatchingPolicy(
        embedder=resolved_embedder, similarity_threshold=threshold
    )

    scorers = [
        SkillsScorer(),
        ExperienceScorer(matching_policy=matching_policy),
        EducationScorer(),
        ProjectsScorer(),
        CertificationsScorer(),
        GrammarScorer(),
        ATSScorer(),
        SemanticVectorScorer(embedder=resolved_embedder),
    ]
    resolved_policy = scoring_policy or ScoringPolicy()
    scoring_engine = ScoringEngine(scorers=scorers, policy=resolved_policy)

    generate_recommendations_use_case = GenerateRecommendationsUseCase(
        llm_provider=resolved_llm_provider
    )
    analyze_resume_use_case = AnalyzeResumeUseCase(
        resume_parser=resolved_resume_parser,
        job_description_parser=resolved_jd_parser,
        scoring_engine=scoring_engine,
        recommendations_use_case=generate_recommendations_use_case,
    )
    match_job_description_use_case = MatchJobDescriptionUseCase(
        scoring_engine=scoring_engine
    )
    rewrite_resume_use_case = RewriteResumeUseCase(
        llm_provider=resolved_llm_provider
    )

    return ApplicationContainer(
        resume_parser=resolved_resume_parser,
        job_description_parser=resolved_jd_parser,
        embedder=resolved_embedder,
        llm_provider=resolved_llm_provider,
        scoring_engine=scoring_engine,
        analyze_resume_use_case=analyze_resume_use_case,
        match_job_description_use_case=match_job_description_use_case,
        generate_recommendations_use_case=generate_recommendations_use_case,
        rewrite_resume_use_case=rewrite_resume_use_case,
    )
