from __future__ import annotations

from app.infrastructure.nlp.spacy_pipeline import get_nlp
from app.infrastructure.parsing.grammar_checker import check_bullets


def test_passive_voice_detected():
    nlp = get_nlp()
    findings, metrics = check_bullets(
        ["The API was built by the team to serve requests"], nlp
    )
    assert any(f.rule_id == "PASSIVE_VOICE" for f in findings)
    assert metrics.passive_voice_ratio == 1.0


def test_active_voice_bullet_has_no_passive_finding():
    nlp = get_nlp()
    findings, metrics = check_bullets(
        ["Built a scalable REST API serving 10k requests per second"], nlp
    )
    assert not any(f.rule_id == "PASSIVE_VOICE" for f in findings)
    assert metrics.passive_voice_ratio == 0.0


def test_weak_verb_flagged():
    nlp = get_nlp()
    findings, _ = check_bullets(["Helped the team ship a new feature"], nlp)
    assert any(f.rule_id == "WEAK_VERB" for f in findings)


def test_quantified_bullet_ratio():
    nlp = get_nlp()
    _, metrics = check_bullets(
        ["Reduced latency by 40%", "Helped the team"], nlp
    )
    assert metrics.quantified_bullet_ratio == 0.5


def test_empty_bullets_returns_default_metrics():
    nlp = get_nlp()
    findings, metrics = check_bullets([], nlp)
    assert findings == []
    assert metrics.passive_voice_ratio == 0.0
