from fastapi import APIRouter

router = APIRouter(prefix="/health", tags=["Gateway Health"])


@router.get("/")
def health_check():
    return {
        "status": "ok",
        "service": "gateway_service"
    }
