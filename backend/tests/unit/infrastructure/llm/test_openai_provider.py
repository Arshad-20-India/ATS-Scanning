from __future__ import annotations

import pytest

from app.infrastructure.llm.openai_provider import (
    OpenAIProvider,
    UngroundedResponseError,
)


def test_explain_evidence_returns_grounded_response(
    make_fake_client, sample_evidence_list
):
    client = make_fake_client(
        ["You're missing Kubernetes and have 3.2 of the 5.0 required years."]
    )
    provider = OpenAIProvider(client=client)

    result = provider.explain_evidence(sample_evidence_list)

    assert "Kubernetes" in result
    assert client.call_count == 1


def test_suggest_improvement_returns_grounded_response(
    make_fake_client, single_failing_evidence
):
    client = make_fake_client(
        ["Try rewriting bullets in active voice to reduce your 0.4 passive ratio."]
    )
    provider = OpenAIProvider(client=client)

    result = provider.suggest_improvement(single_failing_evidence)

    assert "passive" in result.lower()
    assert client.call_count == 1


def test_retries_once_on_ungrounded_response_then_succeeds(
    make_fake_client, sample_evidence_list
):
    client = make_fake_client(
        [
            "You need 10 years of experience.",  # ungrounded (10 not in evidence)
            "You have 3.2 of the 5.0 required years.",  # grounded, second attempt
        ]
    )
    provider = OpenAIProvider(client=client, max_retries=1)

    result = provider.explain_evidence(sample_evidence_list)

    assert result == "You have 3.2 of the 5.0 required years."
    assert client.call_count == 2
    # second prompt must include the retry reminder
    second_call_messages = client.received_prompts[1]["messages"]
    user_message = next(m for m in second_call_messages if m["role"] == "user")
    assert "IMPORTANT" in user_message["content"]


def test_raises_ungrounded_error_after_exhausting_retries(
    make_fake_client, sample_evidence_list
):
    client = make_fake_client(
        [
            "You need 10 years of experience.",
            "Actually you need 15 years minimum.",
        ]
    )
    provider = OpenAIProvider(client=client, max_retries=1)

    with pytest.raises(UngroundedResponseError):
        provider.explain_evidence(sample_evidence_list)

    assert client.call_count == 2  # exactly max_retries + 1 attempts, no more


def test_zero_retries_fails_fast_on_first_ungrounded_response(
    make_fake_client, sample_evidence_list
):
    client = make_fake_client(["You need 10 years of experience."])
    provider = OpenAIProvider(client=client, max_retries=0)

    with pytest.raises(UngroundedResponseError):
        provider.explain_evidence(sample_evidence_list)

    assert client.call_count == 1


def test_uses_configured_model_name(make_fake_client, sample_evidence_list):
    client = make_fake_client(["You have 3.2 of the 5.0 required years."])
    provider = OpenAIProvider(client=client, model_name="gpt-4o-mini")

    provider.explain_evidence(sample_evidence_list)

    assert client.received_prompts[0]["model"] == "gpt-4o-mini"


def test_max_tokens_forwarded_to_client(make_fake_client, single_failing_evidence):
    client = make_fake_client(["Fix your passive voice, currently at 0.4."])
    provider = OpenAIProvider(client=client)

    provider.suggest_improvement(single_failing_evidence, max_tokens=123)

    assert client.received_prompts[0]["max_tokens"] == 123
