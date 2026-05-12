from uuid import uuid4

import httpx


GATEWAY_SERVICE_URL = "http://127.0.0.1:8002"


def create_gateway_access_token_for_test_user() -> str:
    email = f"phase9-gateway-{uuid4().hex}@example.com"
    password = "TestPassword123"

    register_response = httpx.post(
        f"{GATEWAY_SERVICE_URL}/api/v1/auth/register",
        json={
            "email": email,
            "password": password,
        },
        timeout=10.0,
    )

    assert register_response.status_code == 201
    assert register_response.json() == {
        "message": "User registered successfully",
    }

    login_response = httpx.post(
        f"{GATEWAY_SERVICE_URL}/api/v1/auth/login",
        json={
            "email": email,
            "password": password,
        },
        timeout=10.0,
    )

    assert login_response.status_code == 200

    login_data = login_response.json()

    assert "access_token" in login_data
    assert login_data["token_type"] == "bearer"

    return login_data["access_token"]


def test_gateway_auth_register_login_and_me():
    request_id = f"phase9-gateway-auth-{uuid4().hex}"
    email = f"phase9-gateway-auth-{uuid4().hex}@example.com"
    password = "TestPassword123"

    register_response = httpx.post(
        f"{GATEWAY_SERVICE_URL}/api/v1/auth/register",
        headers={
            "X-Request-ID": request_id,
        },
        json={
            "email": email,
            "password": password,
        },
        timeout=10.0,
    )

    assert register_response.status_code == 201
    assert register_response.headers["X-Request-ID"] == request_id

    login_response = httpx.post(
        f"{GATEWAY_SERVICE_URL}/api/v1/auth/login",
        json={
            "email": email,
            "password": password,
        },
        timeout=10.0,
    )

    assert login_response.status_code == 200

    access_token = login_response.json()["access_token"]

    me_response = httpx.get(
        f"{GATEWAY_SERVICE_URL}/api/v1/auth/me",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
        timeout=10.0,
    )

    assert me_response.status_code == 200

    me_data = me_response.json()

    assert me_data["email"] == email
    assert me_data["is_active"] is True
    assert isinstance(me_data["id"], int)


def test_gateway_upload_list_and_download_file():
    access_token = create_gateway_access_token_for_test_user()

    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    filename = f"phase9-gateway-upload-{uuid4().hex}.txt"
    file_content = b"Phase 9 gateway upload integration test content."

    upload_response = httpx.post(
        f"{GATEWAY_SERVICE_URL}/api/v1/uploads/",
        headers=headers,
        files={
            "file": (
                filename,
                file_content,
                "text/plain",
            )
        },
        timeout=15.0,
    )

    assert upload_response.status_code == 200
    assert "X-Request-ID" in upload_response.headers

    upload_data = upload_response.json()

    assert upload_data["message"] == "File uploaded successfully"

    uploaded_file = upload_data["file"]

    assert isinstance(uploaded_file["id"], int)
    assert uploaded_file["filename"] == filename
    assert uploaded_file["content_type"] == "text/plain"
    assert uploaded_file["file_size"] == len(file_content)
    assert uploaded_file["file_path"].startswith(f"users/{uploaded_file['user_id']}/")
    assert uploaded_file["file_path"].endswith(f"-{filename}")

    file_id = uploaded_file["id"]

    list_response = httpx.get(
        f"{GATEWAY_SERVICE_URL}/api/v1/uploads/",
        headers=headers,
        timeout=10.0,
    )

    assert list_response.status_code == 200

    list_data = list_response.json()

    assert list_data["message"] == "Files retrieved successfully"
    assert list_data["count"] >= 1

    matching_files = [
        file for file in list_data["files"]
        if file["id"] == file_id
    ]

    assert len(matching_files) == 1
    assert matching_files[0]["filename"] == filename
    assert matching_files[0]["file_path"] == uploaded_file["file_path"]

    download_response = httpx.get(
        f"{GATEWAY_SERVICE_URL}/api/v1/uploads/{file_id}",
        headers=headers,
        timeout=15.0,
    )

    assert download_response.status_code == 200
    assert download_response.content == file_content
    assert download_response.headers["content-type"].startswith("text/plain")
    assert filename in download_response.headers["content-disposition"]
    assert "X-Request-ID" in download_response.headers


def test_gateway_upload_without_token_returns_403():
    response = httpx.post(
        f"{GATEWAY_SERVICE_URL}/api/v1/uploads/",
        files={
            "file": (
                "gateway-missing-token.txt",
                b"Gateway missing token test content.",
                "text/plain",
            )
        },
        timeout=10.0,
    )

    assert response.status_code == 403
    assert "X-Request-ID" in response.headers


def test_gateway_allows_configured_cors_origin():
    response = httpx.options(
        f"{GATEWAY_SERVICE_URL}/api/v1/auth/login",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Authorization, Content-Type, X-Request-ID",
        },
        timeout=10.0,
    )

    assert response.status_code == 200
    assert response.headers["access-control-allow-origin"] == "http://localhost:3000"


def test_gateway_blocks_unconfigured_cors_origin():
    response = httpx.options(
        f"{GATEWAY_SERVICE_URL}/api/v1/auth/login",
        headers={
            "Origin": "http://malicious.example.com",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Authorization, Content-Type, X-Request-ID",
        },
        timeout=10.0,
    )

    assert response.status_code == 400
    assert "access-control-allow-origin" not in response.headers


def test_gateway_adds_security_headers():
    response = httpx.get(
        f"{GATEWAY_SERVICE_URL}/api/v1/health/",
        timeout=10.0,
    )

    assert response.status_code == 200
    assert response.headers["x-content-type-options"] == "nosniff"
    assert response.headers["x-frame-options"] == "DENY"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert response.headers["permissions-policy"] == "camera=(), microphone=(), geolocation=()"


def test_gateway_rejects_oversized_upload_request():
    access_token = create_gateway_access_token_for_test_user()

    oversized_content = b"x" * ((6 * 1024 * 1024) + 1)

    response = httpx.post(
        f"{GATEWAY_SERVICE_URL}/api/v1/uploads/",
        headers={
            "Authorization": f"Bearer {access_token}",
        },
        files={
            "file": (
                "gateway-oversized-file.txt",
                oversized_content,
                "text/plain",
            )
        },
        timeout=15.0,
    )

    assert response.status_code == 413
    assert response.json() == {
        "detail": "Request body is too large",
    }
    assert "X-Request-ID" in response.headers
