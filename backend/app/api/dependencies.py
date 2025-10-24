"""API dependencies for authentication and authorization."""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.user import User
from app.services.auth_service import AuthService

# HTTP Bearer token security scheme
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User:
    """
    Get current authenticated user from JWT token.

    This dependency extracts and validates the JWT token from the
    Authorization header, then returns the associated user.

    Args:
        credentials: HTTP Bearer credentials from Authorization header
        db: Database session

    Returns:
        User model instance for authenticated user

    Raises:
        HTTPException: 401 if token is missing, invalid, expired, or user not found
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials

    try:
        auth_service = AuthService(db)
        user = await auth_service.verify_access_token(token)
        return user

    except ValueError as e:
        # Token validation errors (expired, invalid, user not found)
        error_message = str(e)

        if "expired" in error_message.lower():
            detail = {
                "type": "token_expired",
                "title": "Token Expired",
                "detail": "Access token has expired. Please refresh your token.",
            }
        elif "user not found" in error_message.lower():
            detail_dict = {
                "type": "user_not_found",
                "title": "User Not Found",
                "detail": "User associated with token no longer exists.",
            }
            detail = detail_dict  # type: ignore[assignment]
        else:
            detail = {
                "type": "invalid_token",
                "title": "Invalid Token",
                "detail": "The provided authentication token is invalid.",
            }

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db),
) -> User | None:
    """
    Get current authenticated user, but return None if not authenticated.

    This is useful for endpoints that have different behavior for
    authenticated vs unauthenticated users, but don't require authentication.

    Args:
        credentials: HTTP Bearer credentials from Authorization header
        db: Database session

    Returns:
        User model instance if authenticated, None otherwise
    """
    if not credentials:
        return None

    try:
        auth_service = AuthService(db)
        user = await auth_service.verify_access_token(credentials.credentials)
        return user
    except ValueError:
        return None
