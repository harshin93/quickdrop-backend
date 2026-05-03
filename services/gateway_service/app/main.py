from fastapi import FastAPI
from services.gateway_service.app.api.v1.router import api_router
from services.gateway_service.app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

app.include_router(api_router, prefix=settings.api_v1_prefix)


@app.get("/")
def root():
    return {
        "message": "QuickDrop Gateway Service is running"
    }
