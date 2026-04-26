from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from services.auth_service.app.core.config import settings


engine = create_engine(settings.AUTH_DATABASE_URL)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()