import os


class Settings:
    def __init__(self) -> None:
        self.APP_NAME: str = os.getenv("APP_NAME", "QuickDrop")
        self.APP_ENV: str = os.getenv("APP_ENV", "local")

        self.POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
        self.POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
        self.POSTGRES_DB: str = os.getenv("POSTGRES_DB", "quickdrop")
        self.POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
        self.POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")

        self.DATABASE_URL: str = os.getenv(
            "DATABASE_URL",
            f"postgresql+psycopg2://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}",
        )

        self.JWT_SECRET: str = os.getenv("JWT_SECRET", "supersecret")
        self.JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")


settings = Settings()