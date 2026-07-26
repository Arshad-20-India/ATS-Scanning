from app.domain.ports.cache import ICache
from app.domain.ports.embedder import IEmbedder
from app.domain.ports.llm_provider import ILLMProvider
from app.domain.ports.parser import IJobDescriptionParser, IResumeParser
from app.domain.ports.repository import (
    IJobDescriptionRepository,
    IResumeRepository,
    JobDescriptionRecord,
    ResumeRecord,
)

__all__ = [
    "IEmbedder",
    "ILLMProvider",
    "IResumeParser",
    "IJobDescriptionParser",
    "ICache",
    "IResumeRepository",
    "IJobDescriptionRepository",
    "ResumeRecord",
    "JobDescriptionRecord",
]
