from fastapi import APIRouter

from services.gateway_service.app.endpoints import auth_proxy
from services.gateway_service.app.endpoints import health
from services.gateway_service.app.endpoints import upload_proxy

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(auth_proxy.router)
api_router.include_router(upload_proxy.router)