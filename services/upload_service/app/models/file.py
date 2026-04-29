from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String

from services.upload_service.app.db.base import Base


class FileMetadata(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)

    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    content_type = Column(String, nullable=True)
    file_size = Column(Integer, nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)