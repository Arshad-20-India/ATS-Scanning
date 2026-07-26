from __future__ import annotations

import io

import docx
import pytest


@pytest.fixture
def sample_resume_docx_bytes() -> bytes:
    document = docx.Document()
    for line in [
        "Jane Smith",
        "jane@example.com | 555-1234",
        "",
        "Experience",
        "Backend Engineer, Acme Corp",
        "Jan 2021 - Jun 2023",
        "- Built a scalable REST API",
        "",
        "Skills",
        "Python, Docker",
    ]:
        document.add_paragraph(line)
    buf = io.BytesIO()
    document.save(buf)
    return buf.getvalue()


def test_upload_requires_auth(api_client, sample_resume_docx_bytes):
    response = api_client.post(
        "/api/v1/resumes",
        files={"file": ("resume.docx", sample_resume_docx_bytes, "application/octet-stream")},
    )
    assert response.status_code == 401


def test_upload_and_parse_resume(api_client, registered_user_token, sample_resume_docx_bytes):
    response = api_client.post(
        "/api/v1/resumes",
        files={"file": ("resume.docx", sample_resume_docx_bytes, "application/octet-stream")},
        headers=registered_user_token["headers"],
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["filename"] == "resume.docx"
    assert body["contact_info"]["full_name"] == "Jane Smith"
    assert body["contact_info"]["email"] == "jane@example.com"
    assert len(body["experience"]) == 1
    assert body["experience"][0]["title"] == "Backend Engineer"


def test_get_resume_by_id(api_client, registered_user_token, sample_resume_docx_bytes):
    upload = api_client.post(
        "/api/v1/resumes",
        files={"file": ("resume.docx", sample_resume_docx_bytes, "application/octet-stream")},
        headers=registered_user_token["headers"],
    )
    resume_id = upload.json()["id"]

    response = api_client.get(
        f"/api/v1/resumes/{resume_id}", headers=registered_user_token["headers"]
    )
    assert response.status_code == 200
    assert response.json()["id"] == resume_id


def test_get_resume_not_found(api_client, registered_user_token):
    response = api_client.get(
        "/api/v1/resumes/00000000-0000-0000-0000-000000000000",
        headers=registered_user_token["headers"],
    )
    assert response.status_code == 404


def test_cannot_get_another_users_resume(api_client, sample_resume_docx_bytes):
    # user A uploads
    api_client.post(
        "/api/v1/auth/register",
        json={"email": "a@example.com", "password": "password123"},
    )
    login_a = api_client.post(
        "/api/v1/auth/login", data={"username": "a@example.com", "password": "password123"}
    )
    headers_a = {"Authorization": f"Bearer {login_a.json()['access_token']}"}

    upload = api_client.post(
        "/api/v1/resumes",
        files={"file": ("resume.docx", sample_resume_docx_bytes, "application/octet-stream")},
        headers=headers_a,
    )
    resume_id = upload.json()["id"]

    # user B tries to access it
    api_client.post(
        "/api/v1/auth/register",
        json={"email": "b@example.com", "password": "password123"},
    )
    login_b = api_client.post(
        "/api/v1/auth/login", data={"username": "b@example.com", "password": "password123"}
    )
    headers_b = {"Authorization": f"Bearer {login_b.json()['access_token']}"}

    response = api_client.get(f"/api/v1/resumes/{resume_id}", headers=headers_b)
    assert response.status_code == 403


def test_list_my_resumes(api_client, registered_user_token, sample_resume_docx_bytes):
    for _ in range(2):
        api_client.post(
            "/api/v1/resumes",
            files={"file": ("resume.docx", sample_resume_docx_bytes, "application/octet-stream")},
            headers=registered_user_token["headers"],
        )

    response = api_client.get("/api/v1/resumes", headers=registered_user_token["headers"])
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_unsupported_file_type_returns_400(api_client, registered_user_token):
    response = api_client.post(
        "/api/v1/resumes",
        files={"file": ("resume.txt", b"plain text resume", "text/plain")},
        headers=registered_user_token["headers"],
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "unsupported_file_type"
