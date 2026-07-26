from __future__ import annotations

import pytest

from app.infrastructure.llm.openai_provider import OpenAIProvider
from app.infrastructure.llm.provider_factory import (
    UnsupportedLLMProviderError,
    get_llm_provider,
)


def test_defaults_to_openai_from_settings():
    provider = get_llm_provider()
    assert isinstance(provider, OpenAIProvider)


def test_explicit_provider_name_selects_correct_adapter():
    provider = get_llm_provider(provider_name="openai")
    assert isinstance(provider, OpenAIProvider)


def test_unsupported_provider_raises_with_helpful_message():
    with pytest.raises(UnsupportedLLMProviderError, match="anthropic"):
        get_llm_provider(provider_name="anthropic")


def test_kwargs_forwarded_to_provider_constructor(make_fake_client):
    client = make_fake_client(["response"])
    provider = get_llm_provider(provider_name="openai", client=client, max_retries=3)
    assert provider._client is client
    assert provider._max_retries == 3
