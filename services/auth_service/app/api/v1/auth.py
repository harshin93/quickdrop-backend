from fastapi import APIRouter, status
from services.auth_service.app.schemas.auth import MessageResponse, UserLogin, UserRegister

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/register", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def register_user(payload: UserRegister):
    return {
        "message": f"User registration endpoint ready for {payload.email}"
    }


@router.post("/login", response_model=MessageResponse)
def login_user(payload: UserLogin):
    return {
        "message": f"Login endpoint ready for {payload.email}"
    }