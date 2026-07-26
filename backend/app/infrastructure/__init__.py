"""
Infrastructure layer: adapters that implement domain ports using real
libraries (pdfplumber, python-docx, spaCy, sentence-transformers,
OpenAI, SQLAlchemy, Celery, ...).

Import rule: this package may import from app.domain freely. Nothing
in app.domain may ever import from here. app.application (Phase 4)
is what wires the two together.
"""
