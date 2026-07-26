from __future__ import annotations

from app.infrastructure.nlp.spacy_pipeline import get_nlp
from app.infrastructure.parsing.contact_extractor import extract_contact_info


def test_extracts_email_phone_linkedin(sample_resume_text):
    nlp = get_nlp()
    contact = extract_contact_info(sample_resume_text, nlp)
    assert contact.email == "jane.smith@example.com"
    assert contact.phone is not None
    assert "linkedin.com/in/janesmith" in contact.linkedin_url


def test_extracts_name_via_first_line_heuristic(sample_resume_text):
    nlp = get_nlp()
    contact = extract_contact_info(sample_resume_text, nlp)
    assert contact.full_name == "Jane Smith"


def test_is_complete_true_when_name_and_email_present(sample_resume_text):
    nlp = get_nlp()
    contact = extract_contact_info(sample_resume_text, nlp)
    assert contact.is_complete() is True


def test_missing_contact_channel_is_incomplete():
    nlp = get_nlp()
    contact = extract_contact_info("Some Person\nNo contact info here.", nlp)
    assert contact.is_complete() is False
