from __future__ import annotations

import pytest

from app.infrastructure.parsing.resume_parser import (
    ResumeParser,
    UnsupportedFileTypeError,
)


def test_parses_full_docx_resume(sample_resume_docx_bytes):
    parser = ResumeParser()
    resume = parser.parse(sample_resume_docx_bytes, "resume.docx")

    assert resume.contact_info.full_name == "Jane Smith"
    assert resume.contact_info.email == "jane.smith@example.com"
    assert {"experience", "education", "skills", "projects", "certifications"} <= set(
        resume.sections_detected
    )
    assert len(resume.experience) == 2
    assert len(resume.education) == 1
    assert len(resume.skills) == 4
    assert len(resume.projects) == 1
    assert len(resume.certifications) == 1
    assert resume.writing_metrics is not None


def test_parses_full_pdf_resume(sample_resume_pdf_bytes):
    parser = ResumeParser()
    resume = parser.parse(sample_resume_pdf_bytes, "resume.pdf")

    assert resume.contact_info.email == "jane.smith@example.com"
    assert len(resume.experience) >= 1
    assert resume.formatting_flags.page_count == 1


def test_docx_with_table_flags_ats_risk(sample_resume_docx_with_table_bytes):
    parser = ResumeParser()
    resume = parser.parse(sample_resume_docx_with_table_bytes, "resume.docx")
    assert resume.formatting_flags.uses_tables is True


def test_unsupported_extension_raises():
    parser = ResumeParser()
    with pytest.raises(UnsupportedFileTypeError):
        parser.parse(b"not a real file", "resume.txt")
