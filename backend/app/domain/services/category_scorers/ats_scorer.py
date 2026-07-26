from __future__ import annotations

from app.domain.entities.evidence import Evidence
from app.domain.entities.job_description import JobDescription
from app.domain.entities.resume import Resume
from app.domain.entities.score import CategoryScore, ScoreCategory
from app.domain.services.category_scorers.base import ICategoryScorer, aggregate_evidence

REQUIRED_SECTIONS = {"experience", "education", "skills"}

NO_TABLES_WEIGHT = 2.0
NO_TEXT_BOXES_WEIGHT = 2.0
STANDARD_FONTS_WEIGHT = 1.0
CONTACT_INFO_WEIGHT = 2.0
SECTIONS_PRESENT_WEIGHT = 2.0
NO_TEXT_IN_IMAGES_WEIGHT = 1.5


class ATSScorer(ICategoryScorer):
    """
    All checks here are structural facts about the parsed document
    (tables, text boxes, fonts, embedded-image text, section headers),
    computed once during parsing in infrastructure and carried on
    Resume.formatting_flags / Resume.sections_detected. This scorer
    only interprets those pre-computed structural facts — it does not
    re-parse the document.
    """

    category = ScoreCategory.ATS_COMPATIBILITY

    def score(self, resume: Resume, job_description: JobDescription) -> CategoryScore:
        flags = resume.formatting_flags

        evidence = [
            Evidence(
                criterion="no_tables_used",
                description="Resume layout avoids tables (tables commonly break ATS text extraction)",
                found_value=flags.uses_tables,
                expected_value=False,
                weight=NO_TABLES_WEIGHT,
                passed=not flags.uses_tables,
                confidence=1.0,
            ),
            Evidence(
                criterion="no_text_boxes",
                description="Resume avoids text boxes / floating elements",
                found_value=flags.uses_text_boxes,
                expected_value=False,
                weight=NO_TEXT_BOXES_WEIGHT,
                passed=not flags.uses_text_boxes,
                confidence=1.0,
            ),
            Evidence(
                criterion="standard_fonts",
                description="Resume uses standard, ATS-safe fonts",
                found_value=flags.non_standard_fonts,
                expected_value=False,
                weight=STANDARD_FONTS_WEIGHT,
                passed=not flags.non_standard_fonts,
                confidence=1.0,
            ),
            Evidence(
                criterion="no_text_embedded_in_images",
                description="Resume does not rely on text embedded inside images (invisible to ATS)",
                found_value=flags.has_images_with_text,
                expected_value=False,
                weight=NO_TEXT_IN_IMAGES_WEIGHT,
                passed=not flags.has_images_with_text,
                confidence=1.0,
            ),
            Evidence(
                criterion="word_count_density",
                description="Total extracted word count density of candidate resume",
                found_value=len(resume.raw_text.split()),
                expected_value="450 - 850 words",
                weight=1.5,
                passed=450 <= len(resume.raw_text.split()) <= 1000,
                confidence=1.0,
            ),
            Evidence(
                criterion="character_count",
                description="Total extracted character count of candidate resume",
                found_value=len(resume.raw_text),
                expected_value="3000 - 6000 chars",
                weight=1.0,
                passed=len(resume.raw_text) > 0,
                confidence=1.0,
            ),
            Evidence(
                criterion="contact_info_extractable",
                description="Contact info (name + email/phone) is reliably extractable",
                found_value=resume.contact_info.is_complete(),
                expected_value=True,
                weight=CONTACT_INFO_WEIGHT,
                passed=resume.contact_info.is_complete(),
                confidence=1.0,
            ),
            self._sections_evidence(resume),
        ]

        return aggregate_evidence(self.category, evidence)

    @staticmethod
    def _sections_evidence(resume: Resume) -> Evidence:
        detected_lower = {s.lower() for s in resume.sections_detected}
        missing = REQUIRED_SECTIONS - detected_lower
        return Evidence(
            criterion="required_sections_present",
            description="Standard sections (experience, education, skills) are detected with recognizable headers",
            found_value=sorted(missing) if missing else "none missing",
            expected_value="no missing sections",
            weight=SECTIONS_PRESENT_WEIGHT,
            passed=not missing,
            confidence=1.0,
        )
