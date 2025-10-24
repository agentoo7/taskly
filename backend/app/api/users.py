"""User endpoints for authenticated user operations."""

from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.auth import UserProfile

router = APIRouter()


@router.get("/me", response_model=UserProfile)
async def get_current_user_profile(
    current_user: User = Depends(get_current_user),
) -> UserProfile:
    """
    Get current authenticated user's profile.

    This endpoint requires authentication via Bearer token in
    the Authorization header.

    Returns:
        UserProfile with user's id, username, email, avatar_url, github_id

    Raises:
        HTTPException: 401 if not authenticated or token invalid
    """
    return UserProfile.model_validate(current_user)
