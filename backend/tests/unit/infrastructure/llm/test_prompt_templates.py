from __future__ import annotations

from app.infrastructure.llm.prompt_templates import (
    build_explain_evidence_prompt,
    build_suggest_improvement_prompt,
)


def test_explain_evidence_prompt_includes_grounding_instruction(sample_evidence_list):
    system_prompt, user_prompt = build_explain_evidence_prompt(sample_evidence_list)
    assert "strictly and only on the evidence" in system_prompt
    assert "Kubernetes" in user_prompt
    assert "3.2" in user_prompt


def test_explain_evidence_prompt_includes_context_when_given(sample_evidence_list):
    _, user_prompt = build_explain_evidence_prompt(
        sample_evidence_list, context="This is for a senior role."
    )
    assert "senior role" in user_prompt


def test_suggest_improvement_prompt_references_failing_criterion(
    single_failing_evidence,
):
    system_prompt, user_prompt = build_suggest_improvement_prompt(
        single_failing_evidence
    )
    assert "passive_voice_ratio" in user_prompt
    assert "strictly and only on the evidence" in system_prompt


def test_suggest_improvement_includes_resume_context_when_given(
    single_failing_evidence,
):
    _, user_prompt = build_suggest_improvement_prompt(
        single_failing_evidence, resume_context="Built stuff using X"
    )
    assert "Built stuff using X" in user_prompt
