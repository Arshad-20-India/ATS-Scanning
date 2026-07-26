"""
RawDocument is the common output shape of both the PDF and DOCX
low-level extractors, before any NLP/section parsing happens. Keeping
this shape identical across formats is what lets everything downstream
(section_detector, contact_extractor, etc.) stay format-agnostic.
"""

from __future__ import annotations

from dataclasses import dataclass

from app.domain.entities.resume import FormattingFlags


@dataclass(frozen=True)
class RawDocument:
    text: str
    formatting_flags: FormattingFlags
