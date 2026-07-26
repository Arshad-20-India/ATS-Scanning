from __future__ import annotations


def test_register_creates_user(api_client):
    response = api_client.post(
        "/api/v1/auth/register",
        json={"email": "new@example.com", "password": "password123"},
    )
    assert response.status_code == 201
    body = response.json()
    assert body["email"] == "new@example.com"
    assert "id" in body


def test_register_duplicate_email_returns_409(api_client):
    payload = {"email": "dup@example.com", "password": "password123"}
    first = api_client.post("/api/v1/auth/register", json=payload)
    assert first.status_code == 201

    second = api_client.post("/api/v1/auth/register", json=payload)
    assert second.status_code == 409


def test_register_short_password_returns_422(api_client):
    response = api_client.post(
        "/api/v1/auth/register", json={"email": "x@example.com", "password": "short"}
    )
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "validation_error"


def test_login_with_correct_credentials_returns_token(api_client):
    api_client.post(
        "/api/v1/auth/register",
        json={"email": "login@example.com", "password": "password123"},
    )
    response = api_client.post(
        "/api/v1/auth/login",
        data={"username": "login@example.com", "password": "password123"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    assert len(body["access_token"]) > 20


def test_login_with_wrong_password_returns_401(api_client):
    api_client.post(
        "/api/v1/auth/register",
        json={"email": "login2@example.com", "password": "password123"},
    )
    response = api_client.post(
        "/api/v1/auth/login",
        data={"username": "login2@example.com", "password": "wrongpassword"},
    )
    assert response.status_code == 401


def test_login_with_nonexistent_email_returns_401(api_client):
    response = api_client.post(
        "/api/v1/auth/login",
        data={"username": "nobody@example.com", "password": "password123"},
    )
    assert response.status_code == 401


def test_me_requires_valid_token(api_client):
    response = api_client.get("/api/v1/auth/me")
    assert response.status_code == 401


def test_me_returns_current_user(api_client, registered_user_token):
    response = api_client.get(
        "/api/v1/auth/me", headers=registered_user_token["headers"]
    )
    assert response.status_code == 200
    assert response.json()["email"] == registered_user_token["email"]


def test_me_with_garbage_token_returns_401(api_client):
    response = api_client.get(
        "/api/v1/auth/me", headers={"Authorization": "Bearer not-a-real-token"}
    )
    assert response.status_code == 401
