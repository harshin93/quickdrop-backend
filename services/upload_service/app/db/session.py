from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from services.upload_service.app.core.config import settings

engine = create_engine(settings.upload_database_url)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)