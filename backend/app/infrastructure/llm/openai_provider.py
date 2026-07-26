"""
ILLMProvider implementation backed by the OpenAI API.

Two design choices mirror SentenceTransformerEmbedder in Phase 2, for
the same reasons:

1. The client is injected, not hardcoded to load at construction time.
   Tests supply a fake object shaped like the OpenAI SDK's client
   (`.chat.completions.create(...)`) instead of making real network
   calls. Production code simply omits `client=` and a real
   `openai.OpenAI()` client is lazily constructed on first use.
2. The real `openai` package is imported lazily inside `_get_client`,
   so importing this module never requires the package to be
   installed unless this adapter is actually instantiated without an
   injected client.

Grounding enforcement: after generation, the response is checked with
response_validator.is_grounded(). If it fails, we retry once with a
stricter reminder appended to the prompt. If it still fails, we raise
UngroundedResponseError rather than returning a response that may
contain fabricated facts -- consistent with the platform-wide rule
that nothing gets served to a user without being traceable to Evidence.
"""

from __future__ import annotations

from typing import List, Optional, Protocol

from app.core.config import settings
from app.domain.entities.evidence import Evidence
from app.domain.ports.llm_provider import ILLMProvider
from app.infrastructure.llm.prompt_templates import (
    build_explain_evidence_prompt,
    build_suggest_improvement_prompt,
)
from app.infrastructure.llm.response_validator import (
    find_ungrounded_numbers,
    is_grounded,
)


class UngroundedResponseError(RuntimeError):
    """
    Raised when the LLM's response could not be verified as grounded
    in the supplied evidence, even after a retry. Callers (the Phase 4
    use case layer) should catch this and fall back to a
    template-based, non-LLM explanation rather than surface nothing.
    """


class _ChatCompletionClient(Protocol):
    chat: "_ChatNamespace"


class _ChatNamespace(Protocol):
    completions: "_CompletionsNamespace"


class _CompletionsNamespace(Protocol):
    def create(self, **kwargs): ...


_RETRY_REMINDER = (
    "\n\nIMPORTANT: your previous response introduced a number or fact "
    "not present in the evidence above. Regenerate your response using "
    "ONLY the facts explicitly given."
)


class OpenAIProvider(ILLMProvider):
    def __init__(
        self,
        client: Optional[_ChatCompletionClient] = None,
        model_name: Optional[str] = None,
        api_key: Optional[str] = None,
        max_retries: int = 1,
    ) -> None:
        self._client = client
        self._model_name = model_name or settings.llm_model_name
        self._api_key = api_key
        self._max_retries = max_retries

    def _get_client(self) -> _ChatCompletionClient:
        if self._client is None:
            from openai import OpenAI  # deferred import, see module docstring

            self._client = OpenAI(api_key=self._api_key)
        return self._client

    def explain_evidence(
        self,
        evidence: List[Evidence],
        *,
        context: Optional[str] = None,
        max_tokens: int = 300,
    ) -> str:
        system_prompt, user_prompt = build_explain_evidence_prompt(evidence, context)
        return self._complete_grounded(system_prompt, user_prompt, evidence, max_tokens)

    def suggest_improvement(
        self,
        failing_evidence: Evidence,
        *,
        resume_context: Optional[str] = None,
        max_tokens: int = 200,
    ) -> str:
        system_prompt, user_prompt = build_suggest_improvement_prompt(
            failing_evidence, resume_context
        )
        return self._complete_grounded(
            system_prompt, user_prompt, [failing_evidence], max_tokens
        )

    def _complete_grounded(
        self,
        system_prompt: str,
        user_prompt: str,
        evidence_list: List[Evidence],
        max_tokens: int,
    ) -> str:
        client = self._get_client()
        prompt = user_prompt

        for attempt in range(self._max_retries + 1):
            response_text = self._call_model(client, system_prompt, prompt, max_tokens)
            if is_grounded(response_text, evidence_list):
                return response_text.strip()
            prompt = user_prompt + _RETRY_REMINDER

        offending = find_ungrounded_numbers(response_text, evidence_list)
        raise UngroundedResponseError(
            f"LLM response could not be grounded in supplied evidence after "
            f"{self._max_retries + 1} attempt(s). Ungrounded numbers: {offending}"
        )

    def _call_model(
        self,
        client: _ChatCompletionClient,
        system_prompt: str,
        user_prompt: str,
        max_tokens: int,
    ) -> str:
        completion = client.chat.completions.create(
            model=self._model_name,
            max_tokens=max_tokens,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return completion.choices[0].message.content or ""
