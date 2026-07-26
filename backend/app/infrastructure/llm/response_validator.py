"""
Programmatic grounding check.

Prompts (prompt_templates.py) tell the model not to invent facts; this
module checks that it actually didn't, for the one class of fact we
can check cheaply and reliably: numbers. If the generated text
contains a numeric token that cannot be traced back to any
Evidence.found_value / Evidence.expected_value (including a percentage
conversion of a 0..1 ratio, since "0.4" and "40%" are the same fact),
we treat the response as ungrounded.

This is intentionally narrow -- it will not catch a fabricated skill
name or a subtly wrong qualitative claim. It is one layer of a
defense-in-depth approach (see prompt_templates.py docstring), not a
complete guarantee.
"""

from __future__ import annotations

import re
from typing import List, Set

from app.domain.entities.evidence import Evidence

_NUMBER_PATTERN = re.compile(r"\d+(?:\.\d+)?")

# Small numbers that commonly appear in natural prose without being
# factual claims (e.g. "one or two things to improve"). Excluding
# these avoids noisy false positives on ordinary connective language.
_BENIGN_NUMBERS = {"0", "1", "2", "3"}


def extract_allowed_numbers(evidence_list: List[Evidence]) -> Set[str]:
    allowed: Set[str] = set(_BENIGN_NUMBERS)

    for evidence in evidence_list:
        for value in (evidence.found_value, evidence.expected_value):
            if value is None:
                continue
            for match in _NUMBER_PATTERN.findall(str(value)):
                allowed.add(match)
                _add_percentage_equivalent(allowed, match)

    return allowed


def _add_percentage_equivalent(allowed: Set[str], number_str: str) -> None:
    try:
        number = float(number_str)
    except ValueError:
        return
    if 0.0 <= number <= 1.0:
        allowed.add(str(round(number * 100)))
        allowed.add(str(int(number * 100)))


def is_grounded(response_text: str, evidence_list: List[Evidence]) -> bool:
    allowed = extract_allowed_numbers(evidence_list)
    response_numbers = set(_NUMBER_PATTERN.findall(response_text))
    ungrounded = response_numbers - allowed
    return len(ungrounded) == 0


def find_ungrounded_numbers(
    response_text: str, evidence_list: List[Evidence]
) -> Set[str]:
    """Returns the offending numbers, for logging/debugging on failure."""
    allowed = extract_allowed_numbers(evidence_list)
    response_numbers = set(_NUMBER_PATTERN.findall(response_text))
    return response_numbers - allowed
