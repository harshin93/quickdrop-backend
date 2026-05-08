from uuid import uuid4

import httpx


AUTH_SERVICE_URL = "http://127.0.0.1:8000"


def test_duplicate_registration_returns_400():
    email = f"phase9-duplicate-{uuid4().hex}@example.com"
    password = "TestPassword123"

    first_response = httpx.post(
        f"{AUTH_SERVICE_URL}/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
        },
        timeout=5.0,
    )

    assert first_response.status_code == 201

    duplicate_response = httpx.post(
        f"{AUTH_SERVICE_URL}/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
        },
        timeout=5.0,
    )

    assert duplicate_response.status_code == 400
    assert duplicate_response.json() == {
        "detail": "User with this email already exists",
    }


def test_login_with_wrong_password_returns_401():
    email = f"phase9-wrong-password-{uuid4().hex}@example.com"

    register_response = httpx.post(
        f"{AUTH_SERVICE_URL}/api/v1/auth/register",
        json={
            "email": email,
            "password": "CorrectPassword123",
        },
        timeout=5.0,
    )

    assert register_response.status_code == 201

    login_response = httpx.post(
        f"{AUTH_SERVICE_URL}/api/v1/auth/login",
        json={
            "email": email,
            "password": "WrongPassword123",
        },
        timeout=5.0,
    )

    assert login_response.status_code == 401
    assert login_response.json() == {
        "detail": "Invalid email or password",
    }


def test_get_me_without_token_returns_403():
    response = httpx.get(
        f"{AUTH_SERVICE_URL}/api/v1/auth/me",
        timeout=5.0,
    )

    assert response.status_code == 403


def test_get_me_with_invalid_token_returns_401():
    response = httpx.get(
        f"{AUTH_SERVICE_URL}/api/v1/auth/me",
        headers={
            "Authorization": "Bearer invalid-token",
        },
        timeout=5.0,
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Could not validate credentials",
    }
