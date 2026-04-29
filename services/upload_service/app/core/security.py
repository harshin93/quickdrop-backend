from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from services.upload_service.app.core.config import settings

security = HTTPBearer()


def get_current_user_id(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> int:
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm]
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication token"
            )

        return int(user_id)

    except (JWTError, ValueError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired authentication token"
        )