import httpx


AUTH_SERVICE_URL = "http://127.0.0.1:8000"
UPLOAD_SERVICE_URL = "http://127.0.0.1:8001"
GATEWAY_SERVICE_URL = "http://127.0.0.1:8002"


def test_auth_service_health_check():
    response = httpx.get(f"{AUTH_SERVICE_URL}/api/v1/health", timeout=5.0)

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_upload_service_health_check():
    response = httpx.get(f"{UPLOAD_SERVICE_URL}/health", timeout=5.0)

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "service": "upload_service",
    }


def test_gateway_service_health_check():
    response = httpx.get(f"{GATEWAY_SERVICE_URL}/api/v1/health/", timeout=5.0)

    assert response.status_code == 200
    assert response.json() == {
        "status": "ok",
        "service": "gateway_service",
    }
    assert "X-Request-ID" in response.headers
