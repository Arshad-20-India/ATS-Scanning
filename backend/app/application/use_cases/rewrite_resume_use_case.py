"""
RewriteResumeUseCase: Takes a parsed resume, job description, and failing evidence recommendations,
and generates an ATS-optimized rewritten resume built from the actual uploaded candidate data.
"""

from typing import List, Optional
import re
from app.domain.entities.resume import Resume
from app.domain.entities.job_description import JobDescription
from app.application.dto import Recommendation
from app.domain.ports.llm_provider import ILLMProvider


class RewriteResumeUseCase:
    def __init__(self, llm_provider: Optional[ILLMProvider] = None) -> None:
        self._llm_provider = llm_provider

    def execute(
        self,
        resume: Resume,
        job_description: JobDescription,
        recommendations: List[Recommendation],
    ) -> str:
        # Check if LLM provider can generate the rewrite
        if self._llm_provider is not None:
            try:
                prompt = self._build_prompt(resume, job_description, recommendations)
                if hasattr(self._llm_provider, "_complete_grounded"):
                    result = self._llm_provider._complete_grounded(
                        system_prompt="You are an expert ATS Resume Optimizer.",
                        user_prompt=prompt,
                        evidence_list=[],
                        max_tokens=1500,
                    )
                    if result and len(result.strip()) > 50:
                        return result
            except Exception:
                pass

        # Fallback: Deterministic ATS Resume Generator using ACTUAL parsed resume text
        return self._generate_template_rewrite(resume, job_description, recommendations)

    def _build_prompt(
        self, resume: Resume, job_description: JobDescription, recommendations: List[Recommendation]
    ) -> str:
        rec_text = "\n".join([f"- {r.category.value}: {r.message}" for r in recommendations])
        return (
            f"Rewrite the following resume into a clean, single-column ATS-friendly Markdown format.\n\n"
            f"Target Job Description:\n{job_description.raw_text[:1500]}\n\n"
            f"Original Candidate Resume Text:\n{resume.raw_text[:2500]}\n\n"
            f"Key Recommendations to incorporate:\n{rec_text}\n\n"
            f"Format requirements:\n"
            f"- Preserve actual candidate name, contact details, work history, and education from original text\n"
            f"- Rephrase bullet points into high-impact action verbs with quantified metrics\n"
            f"- Standard headers: CONTACT, PROFESSIONAL SUMMARY, SKILLS, EXPERIENCE, EDUCATION, HONORS & AWARDS"
        )

    def _generate_template_rewrite(
        self, resume: Resume, job_description: JobDescription, recommendations: List[Recommendation]
    ) -> str:
        raw = resume.raw_text.strip()
        lines = [line.strip() for line in raw.splitlines() if line.strip()]

        # 1. Candidate Name
        c = resume.contact_info
        name = c.full_name
        if not name or name == "YOUR FULL NAME":
            name = lines[0] if lines else "CANDIDATE NAME"

        # 2. Contact Line
        contact_parts = []
        if c.location:
            contact_parts.append(c.location)
        if c.phone:
            contact_parts.append(c.phone)
        if c.email:
            contact_parts.append(c.email)
        if c.linkedin_url:
            contact_parts.append(c.linkedin_url)
        contact_line = " | ".join(contact_parts) if contact_parts else (lines[1] if len(lines) > 1 else "Contact Information")

        # 3. Core Skills
        extracted_skills = [s.name for s in resume.skills]
        jd_skills = [req.phrase for req in job_description.requirements if req.category.value == "skills"]
        combined_skills = list(dict.fromkeys(extracted_skills + jd_skills))
        skills_str = ", ".join(combined_skills) if combined_skills else "Technical & Domain Skills"

        # 4. Work Experience & Raw Blocks
        exp_lines = []
        if resume.experience:
            for exp in resume.experience:
                title = exp.title or "Professional Role"
                company = exp.company or ""
                header = f"### {title}" + (f" | {company}" if company else "")
                bullets = exp.bullets or ["Delivered high-impact projects contributing to organizational goals."]
                bullet_str = "\n".join([f"  * {b}" for b in bullets])
                exp_lines.append(f"{header}\n{bullet_str}")

        # If no structured experience parsed, extract raw text lines
        if not exp_lines and len(lines) > 2:
            body_text = "\n".join(lines[2:20])
            exp_lines.append(f"### Relevant Experience & Background\n  * {body_text[:400]}")

        experience_block = "\n\n".join(exp_lines)

        # 5. Education
        edu_lines = []
        if resume.education:
            for ed in resume.education:
                degree = ed.degree or "Degree"
                inst = ed.institution or "University"
                edu_lines.append(f"* **{degree}** - {inst}")
        if not edu_lines:
            edu_lines.append("* **Degree & Education** - Extracted from candidate profile")
        education_block = "\n".join(edu_lines)

        # Recommendations incorporation
        rec_summary = "; ".join([r.message for r in recommendations[:2]])
        summary_text = f"Accomplished professional with proven domain expertise. {rec_summary}"

        markdown = f"""# {name}
{contact_line}

---

## PROFESSIONAL SUMMARY
{summary_text}

---

## CORE TECHNICAL SKILLS & COMPETENCIES
**Skills:** {skills_str}

---

## PROFESSIONAL EXPERIENCE

{experience_block}

---

## EDUCATION & CREDENTIALS
{education_block}
"""
        return markdown.strip()
