from fastapi import APIRouter, Depends, HTTPException, status
from services.auth_service.app.api.v1.dependencies import get_current_user
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm

from services.auth_service.app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from services.auth_service.app.db.dependencies import get_db
from services.auth_service.app.models.user import User
from services.auth_service.app.schemas.auth import (
    MessageResponse,
    TokenResponse,
    UserLogin,
    UserRegister,
)
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post(
    "/register",
    response_model=MessageResponse,
    status_code=status.HTTP_201_CREATED,
)
def register_user(payload: UserRegister, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == payload.email).first()
    logger.info("Registration attempt for email=%s", payload.email)

    if existing_user:
        logger.warning("Registration failed: email already exists email=%s", payload.email)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )
    
    new_user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    logger.info("User registered successfully user_id=%s email=%s", new_user.id, new_user.email)

    return {"message": "User registered successfully"}


@router.post("/login", response_model=TokenResponse)
def login_user(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    logger.info("Login attempt for email=%s", payload.email)

    if not user:
        logger.warning("Login failed for email=%s", payload.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not verify_password(payload.password, user.hashed_password):
        logger.warning("Login failed for email=%s", payload.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )
    
    access_token = create_access_token(subject=str(user.id))
    logger.info("Login successful user_id=%s email=%s", user.id, user.email)

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
    

@router.post("/token", response_model=TokenResponse)
def swagger_login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user:
        logger.warning("Login failed for email=%s", payload.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not verify_password(form_data.password, user.hashed_password):
        logger.warning("Login failed for email=%s", payload.email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(subject=str(user.id))

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }
    
@router.get("/me")
def get_me(current_user: User = Depends(get_current_user)):
    logger.info("Authenticated user profile requested user_id=%s email=%s", current_user.id, current_user.email)
    return {
        "id": current_user.id,
        "email": current_user.email,
        "is_active": current_user.is_active,
        "created_at": current_user.created_at,
    }
    