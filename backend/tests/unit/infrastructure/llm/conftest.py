from __future__ import annotations

from typing import List

import pytest

from app.domain.entities.evidence import Evidence


class _FakeMessage:
    def __init__(self, content: str) -> None:
        self.content = content


class _FakeChoice:
    def __init__(self, content: str) -> None:
        self.message = _FakeMessage(content)


class _FakeCompletion:
    def __init__(self, content: str) -> None:
        self.choices = [_FakeChoice(content)]


class _FakeCompletionsNamespace:
    """
    Returns a scripted sequence of responses, one per call, so tests
    can simulate "first response is ungrounded, retry succeeds"
    scenarios. If the script runs out, repeats the last response.
    """

    def __init__(self, responses: List[str]) -> None:
        self._responses = responses
        self._call_count = 0
        self.received_prompts: List[dict] = []

    def create(self, **kwargs):
        self.received_prompts.append(kwargs)
        idx = min(self._call_count, len(self._responses) - 1)
        content = self._responses[idx]
        self._call_count += 1
        return _FakeCompletion(content)


class _FakeChatNamespace:
    def __init__(self, responses: List[str]) -> None:
        self.completions = _FakeCompletionsNamespace(responses)


class FakeOpenAIClient:
    """Mimics the shape of openai.OpenAI() enough for OpenAIProvider to use."""

    def __init__(self, responses: List[str]) -> None:
        self.chat = _FakeChatNamespace(responses)

    @property
    def call_count(self) -> int:
        return self.chat.completions._call_count

    @property
    def received_prompts(self) -> List[dict]:
        return self.chat.completions.received_prompts


@pytest.fixture
def make_fake_client():
    def _make(responses: List[str]) -> FakeOpenAIClient:
        return FakeOpenAIClient(responses)

    return _make


@pytest.fixture
def sample_evidence_list() -> List[Evidence]:
    return [
        Evidence(
            criterion="required_skill_present",
            description="Required skill 'Kubernetes' not found in resume",
            found_value=False,
            expected_value=True,
            weight=2.0,
            passed=False,
        ),
        Evidence(
            criterion="years_required_vs_found",
            description="Total years of professional experience",
            found_value=3.2,
            expected_value=5.0,
            weight=3.0,
            passed=False,
        ),
    ]


@pytest.fixture
def single_failing_evidence() -> Evidence:
    return Evidence(
        criterion="passive_voice_ratio",
        description="Proportion of resume bullets written in passive voice",
        found_value=0.4,
        expected_value="<= 0.15",
        weight=1.0,
        passed=False,
    )
