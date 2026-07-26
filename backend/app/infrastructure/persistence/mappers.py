"""
Domain entity <-> dict mapping for JSONB persistence.

Domain entities (Phase 1) are frozen dataclasses that know nothing
about SQLAlchemy or JSON -- correctly so, per Clean Architecture. This
module is the explicit, hand-written translation boundary. It's
intentionally NOT generic (no dataclasses.asdict() + a clever
recursive reconstructor) because generic reconstruction of nested
dataclasses with Optional[date] fields and enums is fragile and hides
exactly the kind of bug that's easy to miss in review. Every field is
named explicitly on both the encode and decode side.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Dict, List, Optional

from app.application.dto import AnalysisResult, Recommendation
from app.domain.entities.evidence import Evidence
from app.domain.entities.job_description import JobDescription, JobRequirement
from app.domain.entities.resume import (
    CertificationEntry,
    ContactInfo,
    DateRange,
    EducationEntry,
    ExperienceEntry,
    FormattingFlags,
    GrammarFinding,
    ProjectEntry,
    Resume,
    Skill,
    WritingMetrics,
)
from app.domain.entities.score import CategoryScore, ScoreCard, ScoreCategory

# ---------------------------------------------------------------- Resume


def _date_range_to_dict(dr: DateRange) -> Dict[str, Any]:
    return {"start": dr.start.isoformat(), "end": dr.end.isoformat() if dr.end else None}


def _date_range_from_dict(d: Dict[str, Any]) -> DateRange:
    return DateRange(
        start=date.fromisoformat(d["start"]),
        end=date.fromisoformat(d["end"]) if d["end"] else None,
    )


def resume_to_dict(resume: Resume) -> Dict[str, Any]:
    return {
        "raw_text": resume.raw_text,
        "contact_info": {
            "full_name": resume.contact_info.full_name,
            "email": resume.contact_info.email,
            "phone": resume.contact_info.phone,
            "location": resume.contact_info.location,
            "linkedin_url": resume.contact_info.linkedin_url,
        },
        "skills": [
            {
                "name": s.name,
                "normalized_name": s.normalized_name,
                "category": s.category,
                "source_section": s.source_section,
            }
            for s in resume.skills
        ],
        "experience": [
            {
                "title": e.title,
                "company": e.company,
                "date_range": _date_range_to_dict(e.date_range),
                "bullets": e.bullets,
                "skills_mentioned": e.skills_mentioned,
            }
            for e in resume.experience
        ],
        "education": [
            {
                "degree": ed.degree,
                "field_of_study": ed.field_of_study,
                "institution": ed.institution,
                "graduation_date": ed.graduation_date.isoformat()
                if ed.graduation_date
                else None,
                "gpa": ed.gpa,
            }
            for ed in resume.education
        ],
        "projects": [
            {
                "name": p.name,
                "description": p.description,
                "technologies": p.technologies,
                "outcomes": p.outcomes,
            }
            for p in resume.projects
        ],
        "certifications": [
            {
                "name": c.name,
                "issuer": c.issuer,
                "date_earned": c.date_earned.isoformat() if c.date_earned else None,
                "expires": c.expires.isoformat() if c.expires else None,
            }
            for c in resume.certifications
        ],
        "sections_detected": resume.sections_detected,
        "formatting_flags": {
            "uses_tables": resume.formatting_flags.uses_tables,
            "uses_text_boxes": resume.formatting_flags.uses_text_boxes,
            "uses_columns": resume.formatting_flags.uses_columns,
            "non_standard_fonts": resume.formatting_flags.non_standard_fonts,
            "has_images_with_text": resume.formatting_flags.has_images_with_text,
            "page_count": resume.formatting_flags.page_count,
        },
        "grammar_findings": [
            {
                "rule_id": g.rule_id,
                "message": g.message,
                "severity": g.severity,
                "span": g.span,
            }
            for g in resume.grammar_findings
        ],
        "writing_metrics": (
            {
                "passive_voice_ratio": resume.writing_metrics.passive_voice_ratio,
                "weak_verb_count": resume.writing_metrics.weak_verb_count,
                "avg_bullet_length_words": resume.writing_metrics.avg_bullet_length_words,
                "quantified_bullet_ratio": resume.writing_metrics.quantified_bullet_ratio,
            }
            if resume.writing_metrics is not None
            else None
        ),
    }


def resume_from_dict(data: Dict[str, Any]) -> Resume:
    contact = data["contact_info"]
    flags = data["formatting_flags"]
    writing_metrics_data = data.get("writing_metrics")

    return Resume(
        raw_text=data["raw_text"],
        contact_info=ContactInfo(
            full_name=contact["full_name"],
            email=contact["email"],
            phone=contact["phone"],
            location=contact["location"],
            linkedin_url=contact["linkedin_url"],
        ),
        skills=[
            Skill(
                name=s["name"],
                normalized_name=s["normalized_name"],
                category=s["category"],
                source_section=s["source_section"],
            )
            for s in data["skills"]
        ],
        experience=[
            ExperienceEntry(
                title=e["title"],
                company=e["company"],
                date_range=_date_range_from_dict(e["date_range"]),
                bullets=e["bullets"],
                skills_mentioned=e["skills_mentioned"],
            )
            for e in data["experience"]
        ],
        education=[
            EducationEntry(
                degree=ed["degree"],
                field_of_study=ed["field_of_study"],
                institution=ed["institution"],
                graduation_date=date.fromisoformat(ed["graduation_date"])
                if ed["graduation_date"]
                else None,
                gpa=ed["gpa"],
            )
            for ed in data["education"]
        ],
        projects=[
            ProjectEntry(
                name=p["name"],
                description=p["description"],
                technologies=p["technologies"],
                outcomes=p["outcomes"],
            )
            for p in data["projects"]
        ],
        certifications=[
            CertificationEntry(
                name=c["name"],
                issuer=c["issuer"],
                date_earned=date.fromisoformat(c["date_earned"])
                if c["date_earned"]
                else None,
                expires=date.fromisoformat(c["expires"]) if c["expires"] else None,
            )
            for c in data["certifications"]
        ],
        sections_detected=data["sections_detected"],
        formatting_flags=FormattingFlags(
            uses_tables=flags["uses_tables"],
            uses_text_boxes=flags["uses_text_boxes"],
            uses_columns=flags["uses_columns"],
            non_standard_fonts=flags["non_standard_fonts"],
            has_images_with_text=flags["has_images_with_text"],
            page_count=flags["page_count"],
        ),
        grammar_findings=[
            GrammarFinding(
                rule_id=g["rule_id"],
                message=g["message"],
                severity=g["severity"],
                span=g["span"],
            )
            for g in data["grammar_findings"]
        ],
        writing_metrics=(
            WritingMetrics(
                passive_voice_ratio=writing_metrics_data["passive_voice_ratio"],
                weak_verb_count=writing_metrics_data["weak_verb_count"],
                avg_bullet_length_words=writing_metrics_data["avg_bullet_length_words"],
                quantified_bullet_ratio=writing_metrics_data["quantified_bullet_ratio"],
            )
            if writing_metrics_data is not None
            else None
        ),
    )


# ---------------------------------------------------------- JobDescription


def job_description_to_dict(jd: JobDescription) -> Dict[str, Any]:
    return {
        "raw_text": jd.raw_text,
        "title": jd.title,
        "required_skills": jd.required_skills,
        "preferred_skills": jd.preferred_skills,
        "min_years_experience": jd.min_years_experience,
        "required_education": jd.required_education,
        "required_certifications": jd.required_certifications,
        "requirements": [
            {"text": r.text, "requirement_type": r.requirement_type, "weight": r.weight}
            for r in jd.requirements
        ],
    }


def job_description_from_dict(data: Dict[str, Any]) -> JobDescription:
    return JobDescription(
        raw_text=data["raw_text"],
        title=data["title"],
        required_skills=data["required_skills"],
        preferred_skills=data["preferred_skills"],
        min_years_experience=data["min_years_experience"],
        required_education=data["required_education"],
        required_certifications=data["required_certifications"],
        requirements=[
            JobRequirement(
                text=r["text"],
                requirement_type=r["requirement_type"],
                weight=r["weight"],
            )
            for r in data["requirements"]
        ],
    )


# --------------------------------------------------------------- ScoreCard


def _evidence_to_dict(evidence: Evidence) -> Dict[str, Any]:
    return {
        "criterion": evidence.criterion,
        "description": evidence.description,
        "found_value": evidence.found_value,
        "expected_value": evidence.expected_value,
        "weight": evidence.weight,
        "passed": evidence.passed,
        "confidence": evidence.confidence,
        "source_span": evidence.source_span,
    }


def _evidence_from_dict(d: Dict[str, Any]) -> Evidence:
    return Evidence(
        criterion=d["criterion"],
        description=d["description"],
        found_value=d["found_value"],
        expected_value=d["expected_value"],
        weight=d["weight"],
        passed=d["passed"],
        confidence=d["confidence"],
        source_span=d["source_span"],
    )


def scorecard_to_dict(scorecard: ScoreCard) -> Dict[str, Any]:
    return {
        "overall_score": scorecard.overall_score,
        "generated_at": scorecard.generated_at.isoformat(),
        "weights_used": {cat.value: w for cat, w in scorecard.weights_used.items()},
        "category_scores": {
            cat.value: {
                "raw_score": cs.raw_score,
                "weight_in_overall": cs.weight_in_overall,
                "evidence": [_evidence_to_dict(e) for e in cs.evidence],
            }
            for cat, cs in scorecard.category_scores.items()
        },
    }


def scorecard_from_dict(data: Dict[str, Any]) -> ScoreCard:
    category_scores = {}
    for cat_value, cs_data in data["category_scores"].items():
        category = ScoreCategory(cat_value)
        category_scores[category] = CategoryScore(
            category=category,
            raw_score=cs_data["raw_score"],
            evidence=[_evidence_from_dict(e) for e in cs_data["evidence"]],
            weight_in_overall=cs_data["weight_in_overall"],
        )

    return ScoreCard(
        overall_score=data["overall_score"],
        category_scores=category_scores,
        weights_used={
            ScoreCategory(cat_value): w for cat_value, w in data["weights_used"].items()
        },
        generated_at=datetime.fromisoformat(data["generated_at"]),
    )


# ---------------------------------------------------------- Recommendations


def recommendations_to_list(recommendations: List[Recommendation]) -> List[Dict[str, Any]]:
    return [
        {
            "criterion": r.criterion,
            "category": r.category.value,
            "message": r.message,
            "is_llm_generated": r.is_llm_generated,
        }
        for r in recommendations
    ]


def recommendations_from_list(data: List[Dict[str, Any]]) -> List[Recommendation]:
    return [
        Recommendation(
            criterion=r["criterion"],
            category=ScoreCategory(r["category"]),
            message=r["message"],
            is_llm_generated=r["is_llm_generated"],
        )
        for r in data
    ]


# ------------------------------------------------------------ AnalysisResult


def analysis_result_to_dict(result: AnalysisResult) -> Dict[str, Any]:
    """Convenience bundle for callers that want to store the whole result
    as one JSON blob rather than the individual pieces (see
    AnalysisModel, which stores resume/JD separately and this only for
    the scorecard+recommendations)."""
    return {
        "scorecard": scorecard_to_dict(result.scorecard),
        "recommendations": recommendations_to_list(result.recommendations),
    }
