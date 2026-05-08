from uuid import uuid4

import httpx


AUTH_SERVICE_URL = "http://127.0.0.1:8000"
UPLOAD_SERVICE_URL = "http://127.0.0.1:8001"


def create_access_token_for_test_user() -> str:
    email = f"phase9-upload-{uuid4().hex}@example.com"
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


def test_upload_list_and_download_file():
    access_token = create_access_token_for_test_user()

    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    filename = f"phase9-upload-{uuid4().hex}.txt"
    file_content = b"Phase 9 upload integration test content."

    upload_response = httpx.post(
        f"{UPLOAD_SERVICE_URL}/api/v1/uploads/",
        headers=headers,
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

    upload_data = upload_response.json()

    assert upload_data["message"] == "File uploaded successfully"

    uploaded_file = upload_data["file"]

    assert isinstance(uploaded_file["id"], int)
    assert isinstance(uploaded_file["user_id"], int)
    assert uploaded_file["filename"] == filename
    assert uploaded_file["content_type"] == "text/plain"
    assert uploaded_file["file_size"] == len(file_content)
    assert uploaded_file["file_path"].startswith(f"users/{uploaded_file['user_id']}/")
    assert uploaded_file["file_path"].endswith(f"-{filename}")

    file_id = uploaded_file["id"]

    list_response = httpx.get(
        f"{UPLOAD_SERVICE_URL}/api/v1/uploads/",
        headers=headers,
        timeout=5.0,
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

    listed_file = matching_files[0]

    assert listed_file["filename"] == filename
    assert listed_file["file_path"] == uploaded_file["file_path"]

    download_response = httpx.get(
        f"{UPLOAD_SERVICE_URL}/api/v1/uploads/{file_id}",
        headers=headers,
        timeout=10.0,
    )

    assert download_response.status_code == 200
    assert download_response.content == file_content
    assert download_response.headers["content-type"].startswith("text/plain")
    assert filename in download_response.headers["content-disposition"]
