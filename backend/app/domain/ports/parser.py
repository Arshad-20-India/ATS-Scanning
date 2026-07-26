from __future__ import annotations

from abc import ABC, abstractmethod

from app.domain.entities.job_description import JobDescription
from app.domain.entities.resume import Resume


class IResumeParser(ABC):
    """
    Port for turning raw file bytes (PDF/DOCX) into a canonical Resume
    entity. Implemented in infrastructure/parsing by format-specific
    adapters (pdfplumber, python-docx) behind a small dispatcher that
    picks the adapter based on file extension/content-type.
    """

    @abstractmethod
    def parse(self, file_bytes: bytes, filename: str) -> Resume:
        raise NotImplementedError


class IJobDescriptionParser(ABC):
    """Port for turning raw JD text into a canonical JobDescription entity."""

    @abstractmethod
    def parse(self, text: str) -> JobDescription:
        raise NotImplementedError
