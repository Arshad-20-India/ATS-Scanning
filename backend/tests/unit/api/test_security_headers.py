from __future__ import annotations


def test_security_headers_present_on_every_response(api_client):
    response = api_client.get("/health")
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["Referrer-Policy"] == "strict-origin-when-cross-origin"
    assert "camera=()" in response.headers["Permissions-Policy"]
    assert "max-age=" in response.headers["Strict-Transport-Security"]


def test_security_headers_present_on_error_responses_too(api_client):
    response = api_client.get("/api/v1/analyses/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404
    assert response.headers["X-Content-Type-Options"] == "nosniff"
