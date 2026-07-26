from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List, Optional

from app.domain.entities.evidence import Evidence


class ILLMProvider(ABC):
    """
    Port for language generation only.

    Deliberately narrow: an ILLMProvider cannot be asked to "score a
    resume" — there is no method for that. It can only be asked to turn
    already-computed Evidence into natural-language text. This is a
    structural guardrail: as long as callers only have access to this
    interface, an LLM cannot become the source of truth for a number.

    The default adapter registered in infrastructure/llm is OpenAI
    (configurable via LLM_PROVIDER env var); Anthropic and local/OSS
    (e.g. Ollama) adapters can be added behind the same interface
    without touching application or domain code.
    """

    @abstractmethod
    def explain_evidence(
        self,
        evidence: List[Evidence],
        *,
        context: Optional[str] = None,
        max_tokens: int = 300,
    ) -> str:
        """
        Produce a short, human-readable explanation grounded strictly
        in the given evidence items. Implementations must include
        instructions (in their system/prompt construction) that forbid
        introducing facts not present in `evidence`.
        """
        raise NotImplementedError

    @abstractmethod
    def suggest_improvement(
        self,
        failing_evidence: Evidence,
        *,
        resume_context: Optional[str] = None,
        max_tokens: int = 200,
    ) -> str:
        """
        Draft one actionable recommendation for a single failing
        Evidence item (e.g. rewrite a weak bullet). Must reference
        `failing_evidence.criterion` so the recommendation is
        traceable back to a specific, displayed check.
        """
        raise NotImplementedError
