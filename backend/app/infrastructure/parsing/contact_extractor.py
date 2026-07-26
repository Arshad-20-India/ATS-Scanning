"""
Contact info extraction.

Email, phone, and LinkedIn URL are extracted with regex -- these have
rigid enough formats that regex is both simpler and more auditable
than an NLP model. Full name is the one field that genuinely benefits
from NER: resumes don't consistently label "Name:", so we look for a
PERSON entity near the top of the document, falling back to a
capitalized-words heuristic on the very first non-empty line.
"""

from __future__ import annotations

import re
from typing import Optional

from spacy.language import Language

from app.domain.entities.resume import ContactInfo

_EMAIL_PATTERN = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
_PHONE_PATTERN = re.compile(
    r"(?:\+?\d{1,3}[\s.-]?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}"
)
_LINKEDIN_PATTERN = re.compile(
    r"(https?://)?(www\.)?linkedin\.com/in/[A-Za-z0-9\-_%]+/?", re.IGNORECASE
)
_HEADER_LINES_TO_SCAN = 5


def extract_contact_info(raw_text: str, nlp: Language) -> ContactInfo:
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    header_block = "\n".join(lines[:_HEADER_LINES_TO_SCAN])

    email_match = _EMAIL_PATTERN.search(raw_text)
    phone_match = _PHONE_PATTERN.search(raw_text)
    linkedin_match = _LINKEDIN_PATTERN.search(raw_text)

    full_name = _extract_name(lines, header_block, nlp)
    location = _extract_location(header_block, nlp)

    return ContactInfo(
        full_name=full_name,
        email=email_match.group(0) if email_match else None,
        phone=phone_match.group(0) if phone_match else None,
        linkedin_url=linkedin_match.group(0) if linkedin_match else None,
        location=location,
    )


def _extract_name(lines: list[str], header_block: str, nlp: Language) -> Optional[str]:
    doc = nlp(header_block)
    person_entities = [
        ent.text.strip() for ent in doc.ents
        if ent.label_ == "PERSON"
        and 1 <= len(ent.text.strip().split()) <= 4
        and not any(kw in ent.text.lower() for kw in ["resume", "cv", "curriculum", "vitae", "summary", "profile", "page"])
    ]
    if person_entities:
        return person_entities[0]

    # Fallback: scan first 3 non-empty lines for a candidate name
    for line in lines[:3]:
        clean_line = re.sub(r"[^\w\s]", "", line).strip()
        words = clean_line.split()
        if (
            1 <= len(words) <= 4
            and all(w[0].isupper() for w in words if w and w[0].isalpha())
            and "@" not in line
            and not any(char.isdigit() for char in line)
            and not any(kw in clean_line.lower() for kw in ["curriculum", "resume", "vitae", "cv", "education", "experience", "summary", "profile", "page"])
        ):
            return clean_line
    return None


def _extract_location(header_block: str, nlp: Language) -> Optional[str]:
    doc = nlp(header_block)
    gpe_entities = [ent.text for ent in doc.ents if ent.label_ == "GPE"]
    return gpe_entities[0] if gpe_entities else None
