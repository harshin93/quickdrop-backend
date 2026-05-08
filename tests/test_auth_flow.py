from uuid import uuid4

import httpx


AUTH_SERVICE_URL = "http://127.0.0.1:8000"


def test_register_login_and_get_current_user():
    email = f"phase9-{uuid4().hex}@example.com"
    password = "TestPassword123"

    register_response = httpx.post(
        f"{AUTH_SERVICE_URL}/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
        },
        timeout=5.0,
    )

    assert register_response.status_code == 201
    assert register_response.json() == {
        "message": "User registered successfully",
    }

    login_response = httpx.post(
        f"{AUTH_SERVICE_URL}/api/v1/auth/login",
        json={
            "email": email,
            "password": password,
        },
        timeout=5.0,
    )

    assert login_response.status_code == 200

    login_data = login_response.json()

    assert "access_token" in login_data
    assert login_data["token_type"] == "bearer"

    access_token = login_data["access_token"]

    me_response = httpx.get(
        f"{AUTH_SERVICE_URL}/api/v1/auth/me",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
        timeout=5.0,
    )

    assert me_response.status_code == 200

    me_data = me_response.json()

    assert me_data["email"] == email
    assert me_data["is_active"] is True
    assert isinstance(me_data["id"], int)
    assert "created_at" in me_data
