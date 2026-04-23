from fastapi import FastAPI

from services.auth_service.app.api.v1.router import api_router
from services.auth_service.app.core.config import APP_NAME, APP_VERSION, API_V1_PREFIX

app = FastAPI(
    title=APP_NAME,
    version=APP_VERSION,
)


@app.get("/")
def root():
    return {
        "service": APP_NAME,
        "version": APP_VERSION,
        "status": "running",
    }


app.include_router(api_router, prefix=API_V1_PREFIX)