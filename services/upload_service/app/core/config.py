from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    upload_database_url: str = (
        "postgresql://quickdrop_user:quickdrop123@localhost:5432/quickdrop_upload"
    )

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    max_upload_size_bytes: int = 5 * 1024 * 1024
    allowed_upload_content_types: tuple[str, ...] = (
        "text/plain",
        "application/pdf",
        "image/png",
        "image/jpeg",
    )

    s3_endpoint_url: str = "http://localhost:9000"
    s3_access_key: str = "quickdrop_minio_user"
    s3_secret_key: str = "quickdrop_minio_password"
    s3_bucket_name: str = "quickdrop-uploads"
    s3_region_name: str = "us-east-1"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()