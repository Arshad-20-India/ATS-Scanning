from __future__ import annotations

import dataclasses
from unittest.mock import patch


def test_oversized_resume_upload_rejected_with_413(api_client):
    # Settings is a frozen dataclass -- can't patch.object() a field on
    # the instance directly (raises FrozenInstanceError). Build a
    # modified copy via dataclasses.replace() and patch the *module-
    # local* `settings` name that analysis_router.py actually reads
    # from (patching app.core.config.settings wouldn't affect
    # analysis_router's already-bound `from ... import settings`).
    from app.api.routers import analysis_router

    tiny_limit_settings = dataclasses.replace(analysis_router.settings, max_upload_size_bytes=10)

    with patch.object(analysis_router, "settings", tiny_limit_settings):
        response = api_client.post(
            "/api/v1/analyses/sync",
            files={
                "resume_file": (
                    "resume.docx",
                    b"this is definitely more than ten bytes of content",
                    "application/octet-stream",
                )
            },
            data={"job_description_text": "Backend Engineer\n\nRequired\n- Python"},
        )
    assert response.status_code == 413


def test_upload_within_limit_is_not_rejected_for_size(api_client):
    import io
    import docx

    document = docx.Document()
    document.add_paragraph("Jane Smith")
    buf = io.BytesIO()
    document.save(buf)

    response = api_client.post(
        "/api/v1/analyses/sync",
        files={"resume_file": ("resume.docx", buf.getvalue(), "application/octet-stream")},
        data={"job_description_text": "Backend Engineer\n\nRequired\n- Python"},
    )
    assert response.status_code != 413
