"""
ResumeParser: the single implementation of IResumeParser that the rest
of the system depends on. It orchestrates every extractor in this
package but contains no parsing logic itself -- if you're looking for
*how* a section gets parsed, look at the individual extractor module,
not here. This file is pure composition, which is what keeps it
readable even as more extractors get added.
"""

from __future__ import annotations

from app.domain.entities.resume import Resume
from app.domain.ports.parser import IResumeParser
from app.domain.services.skill_normalizer import SkillNormalizer
from app.infrastructure.nlp.spacy_pipeline import get_nlp
from app.infrastructure.parsing.certification_extractor import extract_certifications
from app.infrastructure.parsing.contact_extractor import extract_contact_info
from app.infrastructure.parsing.docx_extractor import extract_docx
from app.infrastructure.parsing.education_extractor import extract_education
from app.infrastructure.parsing.experience_extractor import extract_experience
from app.infrastructure.parsing.grammar_checker import check_bullets
from app.infrastructure.parsing.image_extractor import extract_image
from app.infrastructure.parsing.pdf_extractor import extract_pdf
from app.infrastructure.parsing.project_extractor import extract_projects
from app.infrastructure.parsing.raw_document import RawDocument
from app.infrastructure.parsing.section_detector import detect_sections
from app.infrastructure.parsing.skills_extractor import extract_skills

_SUPPORTED_EXTENSIONS = {
    ".pdf": extract_pdf,
    ".docx": extract_docx,
    ".png": extract_image,
    ".jpg": extract_image,
    ".jpeg": extract_image,
}


class UnsupportedFileTypeError(ValueError):
    pass


class InvalidResumeDocumentError(ValueError):
    """Raised when an uploaded document is not a candidate resume/CV."""
    pass


RESUME_KEYWORDS = {
    "experience", "education", "skills", "projects", "summary", "employment",
    "work history", "certifications", "qualifications", "objective", "background",
    "responsibilities", "technologies", "bachelor", "master", "university",
    "curriculum vitae", "resume", "cv", "developer", "engineer", "manager",
    "analyst", "specialist", "coordinator", "director", "associate", "contact",
    "phone", "email", "linkedin", "profile", "degree", "diploma", "gpa"
}


def validate_is_resume(text: str) -> None:
    words = text.split()
    if len(words) < 25:
        raise InvalidResumeDocumentError(
            "Uploaded file contains insufficient text to be a candidate resume (less than 25 words)."
        )

    text_lower = text.lower()
    matches = sum(1 for kw in RESUME_KEYWORDS if kw in text_lower)
    
    if matches < 3:
        raise InvalidResumeDocumentError(
            "Uploaded document does not appear to be a candidate resume/CV. "
            "Please upload a valid candidate resume containing work experience, skills, education, or contact details."
        )


class ResumeParser(IResumeParser):
    def __init__(self, skill_normalizer: SkillNormalizer | None = None) -> None:
        self._skill_normalizer = skill_normalizer or SkillNormalizer()

    def parse(self, file_bytes: bytes, filename: str) -> Resume:
        raw_document = self._extract_raw(file_bytes, filename)
        validate_is_resume(raw_document.text)
        sections = detect_sections(raw_document.text)
        nlp = get_nlp()

        contact_info = extract_contact_info(raw_document.text, nlp)
        skills = extract_skills(sections.get("skills", ""), self._skill_normalizer, full_raw_text=raw_document.text)
        experience = extract_experience(sections.get("experience", ""))
        education = extract_education(sections.get("education", ""))
        projects = extract_projects(sections.get("projects", ""))
        certifications = extract_certifications(sections.get("certifications", ""))

        all_bullets = [b for entry in experience for b in entry.bullets]
        grammar_findings, writing_metrics = check_bullets(all_bullets, nlp)

        return Resume(
            raw_text=raw_document.text,
            contact_info=contact_info,
            skills=skills,
            experience=experience,
            education=education,
            projects=projects,
            certifications=certifications,
            sections_detected=list(sections.keys()),
            formatting_flags=raw_document.formatting_flags,
            grammar_findings=grammar_findings,
            writing_metrics=writing_metrics,
        )

    @staticmethod
    def _extract_raw(file_bytes: bytes, filename: str) -> RawDocument:
        extension = "." + filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
        extractor = _SUPPORTED_EXTENSIONS.get(extension)
        if extractor is None:
            raise UnsupportedFileTypeError(
                f"Unsupported file type '{extension}'. "
                f"Supported: {sorted(_SUPPORTED_EXTENSIONS)}"
            )
        return extractor(file_bytes)
