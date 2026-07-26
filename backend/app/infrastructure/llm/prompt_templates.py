"""
Prompt construction for the LLM provider.

Every prompt built here carries the same non-negotiable instruction:
the model may only reference facts present in the supplied Evidence.
This is a defense-in-depth layer, not the only one -- response_validator.py
provides a second, programmatic check after generation. Neither layer
alone is airtight against a determined jailbreak; together with the
structural guarantee that ILLMProvider methods require Evidence as
input (see the port docstring), this is the honest, three-layer
approach: can't originate a score (structural), told not to invent
facts (prompt), checked for invented numbers (validator).
"""

from __future__ import annotations

from typing import List, Optional, Tuple

from app.domain.entities.evidence import Evidence

_GROUNDING_INSTRUCTION = (
    "You must base your response strictly and only on the evidence "
    "provided below. Do not introduce any fact, number, skill, date, "
    "or claim that is not explicitly present in the evidence. If the "
    "evidence is insufficient to make a strong statement, say so "
    "plainly rather than filling the gap with a plausible-sounding "
    "guess."
)


def _format_evidence(evidence: List[Evidence]) -> str:
    lines = []
    for e in evidence:
        status = "PASSED" if e.passed else "FAILED"
        lines.append(
            f"- [{status}] {e.criterion}: {e.description} "
            f"(found={e.found_value!r}, expected={e.expected_value!r}, "
            f"confidence={e.confidence})"
        )
    return "\n".join(lines)


def build_explain_evidence_prompt(
    evidence: List[Evidence], context: Optional[str] = None
) -> Tuple[str, str]:
    system_prompt = (
        "You are a resume-evaluation assistant. You explain evaluation "
        "results to job candidates in a clear, encouraging, professional "
        "tone. " + _GROUNDING_INSTRUCTION
    )

    context_block = f"\nAdditional context: {context}\n" if context else ""
    user_prompt = (
        f"Explain the following evaluation evidence in 2-4 sentences of "
        f"plain prose, suitable to show directly to the candidate. "
        f"Do not repeat the raw evidence format; write natural language."
        f"{context_block}\n"
        f"Evidence:\n{_format_evidence(evidence)}"
    )
    return system_prompt, user_prompt


def build_suggest_improvement_prompt(
    failing_evidence: Evidence, resume_context: Optional[str] = None
) -> Tuple[str, str]:
    system_prompt = (
        "You are a resume-writing coach. You give specific, actionable "
        "advice to help a candidate address one identified gap. "
        + _GROUNDING_INSTRUCTION
    )

    context_block = (
        f"\nRelevant resume excerpt: {resume_context}\n" if resume_context else ""
    )
    user_prompt = (
        f"The candidate failed the following check. Write one short, "
        f"actionable recommendation (1-3 sentences) that explains what "
        f"to change and why, referencing only the facts below."
        f"{context_block}\n"
        f"Failing check: {failing_evidence.criterion}\n"
        f"Description: {failing_evidence.description}\n"
        f"Found: {failing_evidence.found_value!r}\n"
        f"Expected: {failing_evidence.expected_value!r}"
    )
    return system_prompt, user_prompt
