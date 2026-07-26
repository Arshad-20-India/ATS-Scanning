"""
Canonical resume model.

This is deliberately *parser-agnostic*: whether the resume came from a
PDF, a DOCX, or (in a future iteration) plain pasted text, it must be
normalized into this shape before it reaches domain services. That
boundary is what lets scoring logic stay ignorant of pdfplumber,
python-docx, or any other library.

Any field that a deterministic parser cannot fill confidently should be
left as None / empty, not guessed — guessing belongs in infrastructure
(and should be flagged with low confidence there), never silently
defaulted in the domain layer.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import List, Optional


@dataclass(frozen=True)
class DateRange:
    start: date
    end: Optional[date] = None  # None means "present" / ongoing

    def __post_init__(self) -> None:
        if self.end is not None and self.end < self.start:
            raise ValueError(
                f"DateRange.end ({self.end}) is before start ({self.start})"
            )

    @property
    def months(self) -> int:
        """Whole months between start and end (or today if ongoing)."""
        effective_end = self.end or date.today()
        return (
            (effective_end.year - self.start.year) * 12
            + (effective_end.month - self.start.month)
        )

    @property
    def is_current(self) -> bool:
        return self.end is None


@dataclass(frozen=True)
class Skill:
    name: str
    normalized_name: str
    category: Optional[str] = None  # e.g. "language", "framework", "tool"
    source_section: Optional[str] = None  # e.g. "Skills", "Experience > Bullet 2"


@dataclass(frozen=True)
class ExperienceEntry:
    title: str
    company: str
    date_range: DateRange
    bullets: List[str] = field(default_factory=list)
    skills_mentioned: List[str] = field(default_factory=list)


@dataclass(frozen=True)
class EducationEntry:
    degree: str  # e.g. "Bachelor of Science"
    field_of_study: str  # e.g. "Computer Science"
    institution: str
    graduation_date: Optional[date] = None
    gpa: Optional[float] = None


@dataclass(frozen=True)
class ProjectEntry:
    name: str
    description: str
    technologies: List[str] = field(default_factory=list)
    outcomes: List[str] = field(default_factory=list)  # quantified achievement bullets


@dataclass(frozen=True)
class CertificationEntry:
    name: str
    issuer: Optional[str] = None
    date_earned: Optional[date] = None
    expires: Optional[date] = None


@dataclass(frozen=True)
class ContactInfo:
    full_name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    linkedin_url: Optional[str] = None

    def is_complete(self) -> bool:
        """
        Minimum bar for ATS parseability: a system that can't reliably
        extract name + at least one contact channel will silently drop
        the candidate, regardless of resume quality.
        """
        has_contact_channel = bool(self.email or self.phone)
        return bool(self.full_name) and has_contact_channel


@dataclass(frozen=True)
class FormattingFlags:
    """
    Structural signals relevant to ATS parseability. These come from
    inspecting the *document structure* (PDF/DOCX object model), not
    the rendered text, so they must be computed in infrastructure at
    parse time and carried through on the Resume entity.
    """

    uses_tables: bool = False
    uses_text_boxes: bool = False
    uses_columns: bool = False
    non_standard_fonts: bool = False
    has_images_with_text: bool = False  # text embedded in images is invisible to ATS
    page_count: int = 1


@dataclass(frozen=True)
class GrammarFinding:
    rule_id: str
    message: str
    severity: str  # "error" | "warning" | "info"
    span: str


@dataclass(frozen=True)
class WritingMetrics:
    passive_voice_ratio: float = 0.0  # 0..1
    weak_verb_count: int = 0
    avg_bullet_length_words: float = 0.0
    quantified_bullet_ratio: float = 0.0  # bullets containing a number/metric


@dataclass(frozen=True)
class Resume:
    raw_text: str
    contact_info: ContactInfo
    skills: List[Skill] = field(default_factory=list)
    experience: List[ExperienceEntry] = field(default_factory=list)
    education: List[EducationEntry] = field(default_factory=list)
    projects: List[ProjectEntry] = field(default_factory=list)
    certifications: List[CertificationEntry] = field(default_factory=list)
    sections_detected: List[str] = field(default_factory=list)
    formatting_flags: FormattingFlags = field(default_factory=FormattingFlags)
    grammar_findings: List[GrammarFinding] = field(default_factory=list)
    writing_metrics: Optional[WritingMetrics] = None

    @property
    def total_experience_months(self) -> int:
        return sum(e.date_range.months for e in self.experience)

    @property
    def total_experience_years(self) -> float:
        return round(self.total_experience_months / 12, 1)
