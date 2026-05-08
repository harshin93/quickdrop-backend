from uuid import uuid4

import httpx


AUTH_SERVICE_URL = "http://127.0.0.1:8000"
UPLOAD_SERVICE_URL = "http://127.0.0.1:8001"


def create_access_token_for_test_user() -> str:
    email = f"phase9-upload-error-{uuid4().hex}@example.com"
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

    login_response = httpx.post(
        f"{AUTH_SERVICE_URL}/api/v1/auth/login",
        json={
            "email": email,
            "password": password,
        },
        timeout=5.0,
    )

    assert login_response.status_code == 200

    return login_response.json()["access_token"]


def upload_test_file(access_token: str) -> dict:
    filename = f"phase9-owned-file-{uuid4().hex}.txt"
    file_content = b"Ownership test file content."

    upload_response = httpx.post(
        f"{UPLOAD_SERVICE_URL}/api/v1/uploads/",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
        files={
            "file": (
                filename,
                file_content,
                "text/plain",
            )
        },
        timeout=10.0,
    )

    assert upload_response.status_code == 200

    return upload_response.json()["file"]


def test_upload_without_token_returns_403():
    response = httpx.post(
        f"{UPLOAD_SERVICE_URL}/api/v1/uploads/",
        files={
            "file": (
                "missing-token.txt",
                b"Missing token test content.",
                "text/plain",
            )
        },
        timeout=5.0,
    )

    assert response.status_code == 403


def test_upload_with_invalid_token_returns_401():
    response = httpx.post(
        f"{UPLOAD_SERVICE_URL}/api/v1/uploads/",
        headers={
            "Authorization": "Bearer invalid-token",
        },
        files={
            "file": (
                "invalid-token.txt",
                b"Invalid token test content.",
                "text/plain",
            )
        },
        timeout=5.0,
    )

    assert response.status_code == 401
    assert response.json() == {
        "detail": "Invalid or expired authentication token",
    }


def test_download_non_existing_file_returns_404():
    access_token = create_access_token_for_test_user()

    response = httpx.get(
        f"{UPLOAD_SERVICE_URL}/api/v1/uploads/999999999",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
        timeout=5.0,
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "File not found",
    }


def test_user_cannot_download_another_users_file():
    owner_access_token = create_access_token_for_test_user()
    other_user_access_token = create_access_token_for_test_user()

    uploaded_file = upload_test_file(owner_access_token)
    file_id = uploaded_file["id"]

    response = httpx.get(
        f"{UPLOAD_SERVICE_URL}/api/v1/uploads/{file_id}",
        headers={
            "Authorization": f"Bearer {other_user_access_token}",
        },
        timeout=5.0,
    )

    assert response.status_code == 404
    assert response.json() == {
        "detail": "File not found",
    }
