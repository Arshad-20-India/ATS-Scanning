"""
Evidence is the single most important entity in this system.

Design contract: no score anywhere in the platform may exist without a
list of Evidence backing it. This is what makes the output explainable
rather than a black-box number. Every Evidence instance answers four
questions for the end user:

    1. What was checked?            -> criterion / description
    2. What did we find?            -> found_value
    3. What were we expecting?      -> expected_value
    4. Did it pass, and how much    -> passed / weight / confidence
       does it matter?

`confidence` is distinct from `passed`: a semantic-similarity match can
pass a threshold at 0.56 confidence, which is meaningfully different
from passing at 0.95 confidence, even though both are "passed=True".
Downstream UI and recommendation generation both use this distinction.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


@dataclass(frozen=True)
class Evidence:
    # Machine-readable identifier, e.g. "required_skill_present",
    # "years_required_vs_found", "passive_voice_ratio". Stable across
    # runs so evidence can be diffed/tracked over time.
    criterion: str

    # Human-readable explanation of what this criterion checks.
    description: str

    # What was actually found in the resume/JD (any JSON-serializable value).
    found_value: Any

    # What was required/expected for a full pass.
    expected_value: Any

    # Relative importance of this evidence item within its category.
    # Weights are compared only within a category, not across categories
    # (cross-category weighting is ScoringPolicy's job).
    weight: float

    # Did this specific criterion pass?
    passed: bool

    # How confident are we in `found_value`? 1.0 for deterministic
    # extraction (e.g. regex-parsed dates), <1.0 for anything derived
    # from semantic similarity or fuzzy matching.
    confidence: float = 1.0

    # Optional pointer back into the source document (a quoted bullet,
    # a section name, etc.) so the UI can highlight exactly where this
    # evidence came from.
    source_span: Optional[str] = None

    def __post_init__(self) -> None:
        if not (0.0 <= self.confidence <= 1.0):
            raise ValueError(
                f"Evidence.confidence must be in [0, 1], got {self.confidence}"
            )
        if self.weight < 0:
            raise ValueError(f"Evidence.weight must be >= 0, got {self.weight}")
