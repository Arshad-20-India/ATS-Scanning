from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Literal, Optional

RequirementType = Literal[
    "required_skill",
    "preferred_skill",
    "experience",
    "education",
    "certification",
]


@dataclass(frozen=True)
class JobRequirement:
    """
    A single free-text requirement extracted from the JD, used for
    semantic matching against resume bullets/projects (see
    MatchingPolicy). Keeping requirement_type lets scorers filter to
    only the requirements relevant to their category instead of
    semantically matching everything against everything.
    """

    text: str
    requirement_type: RequirementType
    weight: float = 1.0

    def __post_init__(self) -> None:
        if self.weight < 0:
            raise ValueError(f"JobRequirement.weight must be >= 0, got {self.weight}")


@dataclass(frozen=True)
class JobDescription:
    raw_text: str
    title: str
    required_skills: List[str] = field(default_factory=list)
    preferred_skills: List[str] = field(default_factory=list)
    min_years_experience: Optional[float] = None
    required_education: Optional[str] = None
    required_certifications: List[str] = field(default_factory=list)
    requirements: List[JobRequirement] = field(default_factory=list)
