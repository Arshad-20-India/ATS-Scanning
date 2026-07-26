from __future__ import annotations

_SAMPLE_JD_TEXT = """Backend Engineer

Required
- Python
- Docker

Preferred
- Kubernetes
"""


def test_create_requires_auth(api_client):
    response = api_client.post("/api/v1/job-descriptions", json={"text": _SAMPLE_JD_TEXT})
    assert response.status_code == 401


def test_create_and_parse_job_description(api_client, registered_user_token):
    response = api_client.post(
        "/api/v1/job-descriptions",
        json={"text": _SAMPLE_JD_TEXT},
        headers=registered_user_token["headers"],
    )
    assert response.status_code == 201, response.text
    body = response.json()
    assert body["title"] == "Backend Engineer"
    assert "Python" in body["required_skills"]
    assert "Kubernetes" in body["preferred_skills"]


def test_text_too_short_returns_422(api_client, registered_user_token):
    response = api_client.post(
        "/api/v1/job-descriptions",
        json={"text": "short"},
        headers=registered_user_token["headers"],
    )
    assert response.status_code == 422


def test_get_by_id(api_client, registered_user_token):
    create = api_client.post(
        "/api/v1/job-descriptions",
        json={"text": _SAMPLE_JD_TEXT},
        headers=registered_user_token["headers"],
    )
    jd_id = create.json()["id"]

    response = api_client.get(
        f"/api/v1/job-descriptions/{jd_id}", headers=registered_user_token["headers"]
    )
    assert response.status_code == 200
    assert response.json()["id"] == jd_id


def test_list_mine(api_client, registered_user_token):
    api_client.post(
        "/api/v1/job-descriptions",
        json={"text": _SAMPLE_JD_TEXT},
        headers=registered_user_token["headers"],
    )
    response = api_client.get(
        "/api/v1/job-descriptions", headers=registered_user_token["headers"]
    )
    assert response.status_code == 200
    assert len(response.json()) == 1
