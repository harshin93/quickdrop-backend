from fastapi import APIRouter

from services.auth_service.app.api.v1 import auth
from services.auth_service.app.endpoints import health

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(auth.router)