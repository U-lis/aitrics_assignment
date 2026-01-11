from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import get_settings

security = HTTPBearer()


def verify_bearer_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> bool:
    """
    Verify Bearer token matches configured token.

    Raises:
        HTTPException 401: If token is invalid or missing
    """
    settings = get_settings()
    if credentials.credentials != settings.BEARER_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return True
