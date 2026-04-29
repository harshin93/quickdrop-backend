from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App metadata
    PROJECT_NAME: str = "QuickDrop Auth Service"
    PROJECT_VERSION: str = "0.1.0"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"

    # Database + Auth
    AUTH_DATABASE_URL: str
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    model_config = SettingsConfigDict(env_file=".env",
        extra = "ignore")

    # Backward compatibility with existing code
    @property
    def app_name(self) -> str:
        return self.PROJECT_NAME

    @property
    def app_version(self) -> str:
        return self.PROJECT_VERSION

    @property
    def debug(self) -> bool:
        return self.DEBUG

    @property
    def api_v1_prefix(self) -> str:
        return self.API_V1_PREFIX


settings = Settings()