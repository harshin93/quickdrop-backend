from fastapi import FastAPI

from services.auth_service.app.api.v1.router import api_router
from services.auth_service.app.core.config import settings
from services.auth_service.app.db.session import Base, engine
from services.auth_service.app.models.user import User
from services.auth_service.app.core.logging import configure_logging



app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

configure_logging()


@app.on_event("startup")
def create_tables():
    Base.metadata.create_all(bind=engine)


app.include_router(api_router, prefix="/api/v1")