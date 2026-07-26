"""
Grammar/writing-quality checking.

Deliberate trade-off: we use spaCy's dependency parse (already loaded
for section/contact extraction) plus a small rule-based heuristic set,
instead of LanguageTool. LanguageTool requires a JVM and either a
bundled ~200MB+ language model or a network call to a public API --
both add real operational weight for a check that, for resume bullets
specifically (short, imperative-style sentences), rule-based heuristics
handle well. This is revisitable: GrammarChecker's output shape
(GrammarFinding / WritingMetrics) is entirely decoupled from how it's
computed, so swapping in LanguageTool later means changing only this
file, not any domain code or scorer.
"""

from __future__ import annotations

import re
from typing import List, Tuple

from spacy.language import Language
from spacy.tokens import Doc

from app.domain.entities.resume import GrammarFinding, WritingMetrics

_WEAK_VERBS = {
    "helped", "worked", "was responsible for", "did", "made", "handled",
    "assisted", "involved in", "participated in",
}
_REPEATED_WORD_PATTERN = re.compile(r"\b(\w+)\s+\1\b", re.IGNORECASE)
_NUMBER_PATTERN = re.compile(r"\d")
_MIN_BULLET_WORDS = 3


def check_bullets(
    bullets: List[str], nlp: Language
) -> Tuple[List[GrammarFinding], WritingMetrics]:
    if not bullets:
        return [], WritingMetrics()

    findings: List[GrammarFinding] = []
    passive_count = 0
    weak_verb_count = 0
    quantified_count = 0
    total_words = 0

    for bullet in bullets:
        doc = nlp(bullet)
        total_words += len(bullet.split())

        if _is_passive(doc):
            passive_count += 1
            findings.append(
                GrammarFinding(
                    rule_id="PASSIVE_VOICE",
                    message="Bullet is written in passive voice; consider an active, "
                    "achievement-led construction (e.g. 'Led...' / 'Built...').",
                    severity="warning",
                    span=bullet,
                )
            )

        weak_verb_hit = _find_weak_verb(bullet)
        if weak_verb_hit:
            weak_verb_count += 1
            findings.append(
                GrammarFinding(
                    rule_id="WEAK_VERB",
                    message=f"'{weak_verb_hit}' is a weak/vague verb; a stronger, "
                    f"specific action verb usually reads better.",
                    severity="info",
                    span=bullet,
                )
            )

        repeated = _REPEATED_WORD_PATTERN.search(bullet)
        if repeated:
            findings.append(
                GrammarFinding(
                    rule_id="REPEATED_WORD",
                    message=f"Repeated word '{repeated.group(1)}' detected.",
                    severity="error",
                    span=bullet,
                )
            )

        if len(bullet.split()) < _MIN_BULLET_WORDS:
            findings.append(
                GrammarFinding(
                    rule_id="FRAGMENT_TOO_SHORT",
                    message="Bullet is unusually short; consider expanding with "
                    "context or a measurable outcome.",
                    severity="warning",
                    span=bullet,
                )
            )

        if _NUMBER_PATTERN.search(bullet):
            quantified_count += 1

    metrics = WritingMetrics(
        passive_voice_ratio=round(passive_count / len(bullets), 3),
        weak_verb_count=weak_verb_count,
        avg_bullet_length_words=round(total_words / len(bullets), 1),
        quantified_bullet_ratio=round(quantified_count / len(bullets), 3),
    )
    return findings, metrics


def _is_passive(doc: Doc) -> bool:
    return any(token.dep_ in ("nsubjpass", "auxpass", "nsubj:pass") for token in doc)


def _find_weak_verb(bullet: str) -> str | None:
    lowered = bullet.lower()
    for verb in _WEAK_VERBS:
        if re.search(rf"\b{re.escape(verb)}\b", lowered):
            return verb
    return None
