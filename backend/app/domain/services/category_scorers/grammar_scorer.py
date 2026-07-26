from __future__ import annotations

from app.domain.entities.evidence import Evidence
from app.domain.entities.job_description import JobDescription
from app.domain.entities.resume import Resume, WritingMetrics
from app.domain.entities.score import CategoryScore, ScoreCategory
from app.domain.services.category_scorers.base import ICategoryScorer, aggregate_evidence

MAX_TOLERABLE_ERRORS = 3
MAX_TOLERABLE_WARNINGS = 8
MAX_PASSIVE_VOICE_RATIO = 0.15

ERROR_COUNT_WEIGHT = 2.0
WARNING_COUNT_WEIGHT = 1.0
PASSIVE_VOICE_WEIGHT = 1.0


class GrammarScorer(ICategoryScorer):
    """
    Grammar/writing-quality checking itself is deterministic (a rule
    engine like LanguageTool runs during parsing, in infrastructure,
    and its output is attached to the Resume entity as
    `grammar_findings` / `writing_metrics`). This scorer's job is only
    to turn those pre-computed findings into weighted Evidence — it
    does not run any NLP itself, keeping the domain layer
    framework-free.
    """

    category = ScoreCategory.GRAMMAR

    def score(self, resume: Resume, job_description: JobDescription) -> CategoryScore:
        errors = [f for f in resume.grammar_findings if f.severity == "error"]
        warnings = [f for f in resume.grammar_findings if f.severity == "warning"]

        evidence = [
            Evidence(
                criterion="grammar_error_count",
                description="Number of grammar errors detected in resume text",
                found_value=len(errors),
                expected_value=f"<= {MAX_TOLERABLE_ERRORS}",
                weight=ERROR_COUNT_WEIGHT,
                passed=len(errors) <= MAX_TOLERABLE_ERRORS,
                confidence=1.0,
            ),
            Evidence(
                criterion="grammar_warning_count",
                description="Number of style/clarity warnings detected",
                found_value=len(warnings),
                expected_value=f"<= {MAX_TOLERABLE_WARNINGS}",
                weight=WARNING_COUNT_WEIGHT,
                passed=len(warnings) <= MAX_TOLERABLE_WARNINGS,
                confidence=1.0,
            ),
        ]

        evidence.append(self._action_verb_strength_evidence(resume.raw_text))

        if resume.writing_metrics is not None:
            evidence.append(self._passive_voice_evidence(resume.writing_metrics))

        return aggregate_evidence(self.category, evidence)

    @staticmethod
    def _action_verb_strength_evidence(raw_text: str) -> Evidence:
        import re
        weak_phrases = ["responsible for", "worked on", "assisted in", "helped with", "handled duties", "tasked with"]
        found_weak = [phrase for phrase in weak_phrases if phrase in raw_text.lower()]
        passed = len(found_weak) == 0

        if passed:
            desc = "Action Verb Strength: Strong action-oriented phrasing detected across resume."
            found_val = "0 weak passive phrases"
            source = "Strong Action Verbs"
        else:
            desc = f"Action Verb Strength: Detected weak passive phrases ({', '.join(found_weak)}). Replace with strong action verbs (e.g. Spearheaded, Engineered, Directed)."
            found_val = f"Weak phrases: {', '.join(found_weak)}"
            source = f"Weak phrase: '{found_weak[0]}'"

        return Evidence(
            criterion="action_verb_strength",
            description=desc,
            found_value=found_val,
            expected_value="0 weak passive phrases",
            weight=1.5,
            passed=passed,
            confidence=1.0,
            source_span=source,
        )

    @staticmethod
    def _passive_voice_evidence(metrics: WritingMetrics) -> Evidence:
        passed = metrics.passive_voice_ratio <= MAX_PASSIVE_VOICE_RATIO
        return Evidence(
            criterion="passive_voice_ratio",
            description="Proportion of resume bullets written in passive voice",
            found_value=round(metrics.passive_voice_ratio, 2),
            expected_value=f"<= {MAX_PASSIVE_VOICE_RATIO}",
            weight=PASSIVE_VOICE_WEIGHT,
            passed=passed,
            confidence=1.0,
        )
