from fastapi import APIRouter
from services.auth_service.app.endpoints import health

api_router = APIRouter()
api_router.include_router(health.router)