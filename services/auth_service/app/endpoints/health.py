from fastapi import APIRouter
from shared.schemas.health import HealthResponse

router = APIRouter()


@router.get("/health", response_model=HealthResponse, tags=["health"])
def health_check():
    return {"status": "ok"}