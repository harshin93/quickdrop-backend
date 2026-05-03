from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "QuickDrop Gateway Service"
    app_version: str = "1.0.0"
    debug: bool = True

    api_v1_prefix: str = "/api/v1"

    auth_service_url: str = "http://127.0.0.1:8000"
    upload_service_url: str = "http://127.0.0.1:8001"


settings = Settings()
