from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    upload_database_url: str = "postgresql://quickdrop_user:quickdrop123@localhost:5432/quickdrop_upload"

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()