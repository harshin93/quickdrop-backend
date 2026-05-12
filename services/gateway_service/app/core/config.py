from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "QuickDrop Gateway Service"
    app_version: str = "1.0.0"
    debug: bool = True

    api_v1_prefix: str = "/api/v1"

    auth_service_url: str = "http://127.0.0.1:8000"
    upload_service_url: str = "http://127.0.0.1:8001"

    gateway_max_upload_request_size_bytes: int = 6 * 1024 * 1024

    cors_allowed_origins: list[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]


settings = Settings()
