"""
Factory for ILLMProvider implementations.

This is the *only* place in the codebase that should know the mapping
from a provider name string to a concrete adapter class. Application
code (Phase 4) depends on `get_llm_provider()` and the `ILLMProvider`
interface -- never on `OpenAIProvider` directly -- so adding Anthropic
or a local/OSS provider later means adding one branch here, not
touching every call site.
"""

from __future__ import annotations

from app.core.config import settings
from app.domain.ports.llm_provider import ILLMProvider
from app.infrastructure.llm.openai_provider import OpenAIProvider

_SUPPORTED_PROVIDERS = {"openai": OpenAIProvider}


class UnsupportedLLMProviderError(ValueError):
    pass


def get_llm_provider(provider_name: str | None = None, **kwargs) -> ILLMProvider:
    name = provider_name or settings.llm_provider
    provider_cls = _SUPPORTED_PROVIDERS.get(name)
    if provider_cls is None:
        raise UnsupportedLLMProviderError(
            f"Unsupported LLM provider '{name}'. "
            f"Supported: {sorted(_SUPPORTED_PROVIDERS)}. "
            f"To add a new provider, implement ILLMProvider and register "
            f"it in _SUPPORTED_PROVIDERS above."
        )
    return provider_cls(**kwargs)
