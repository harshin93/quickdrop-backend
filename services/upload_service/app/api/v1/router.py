from fastapi import APIRouter

from services.upload_service.app.api.v1 import uploads

api_router = APIRouter()

api_router.include_router(uploads.router)