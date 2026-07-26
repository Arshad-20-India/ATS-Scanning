"""
Domain layer.

This package is intentionally framework-free: no FastAPI, no SQLAlchemy,
no spaCy, no HTTP clients. Everything here is pure Python (dataclasses,
enums, plain functions/classes) so it can be unit-tested without mocks
and reused regardless of what web framework, database, or NLP library
sits in the infrastructure layer.

Rule enforced by convention (and by import-linter in CI, see
pyproject.toml): nothing under app/domain may import from
app/infrastructure or app/api.
"""
