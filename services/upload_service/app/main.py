from fastapi import FastAPI

from services.upload_service.app.api.v1.router import api_router
from services.upload_service.app.db.base import Base
from services.upload_service.app.db.session import engine
from services.upload_service.app.models.file import FileMetadata
from services.upload_service.app.core.logging import configure_logging

configure_logging()

app = FastAPI(
    title="QuickDrop Upload Service",
    version="1.0.0",
    description="Upload service for QuickDrop backend"
)


@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "upload_service"
    }


app.include_router(api_router, prefix="/api/v1")