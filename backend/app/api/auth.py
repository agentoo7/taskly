"""Authentication endpoints for GitHub OAuth and JWT management."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.schemas.auth import (
    LogoutRequest,
    RefreshTokenRequest,
    RefreshTokenResponse,
    TokenResponse,
)
from app.services.auth_service import AuthService

router = APIRouter()


def get_auth_service(db: AsyncSession = Depends(get_db)) -> AuthService:
    """
    Dependency for getting AuthService instance.

    Args:
        db: Database session

    Returns:
        AuthService instance
    """
    return AuthService(db)


@router.get("/github/login")
async def github_login() -> RedirectResponse:
    """
    Initiate GitHub OAuth flow by redirecting to GitHub authorization page.

    Query Parameters:
        None

    Returns:
        Redirect to GitHub OAuth authorization page
    """
    # Build GitHub OAuth authorization URL
    github_auth_url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={settings.GITHUB_CLIENT_ID}"
        f"&redirect_uri={settings.CORS_ORIGINS[0]}/auth/callback"
        f"&scope=user:email"
    )

    return RedirectResponse(url=github_auth_url)


@router.get("/github/callback", response_model=TokenResponse)
async def github_callback(
    code: str = Query(..., description="OAuth authorization code from GitHub"),
    auth_service: AuthService = Depends(get_auth_service),
) -> TokenResponse:
    """
    Handle GitHub OAuth callback and issue JWT tokens.

    This endpoint:
    1. Exchanges authorization code for GitHub access token
    2. Fetches user profile from GitHub API
    3. Creates or updates user in database
    4. Issues JWT access and refresh tokens

    Query Parameters:
        code: OAuth authorization code from GitHub

    Returns:
        TokenResponse with access_token, refresh_token, token_type, expires_in

    Raises:
        HTTPException: 400 if code is invalid or GitHub API fails
        HTTPException: 500 if unexpected error occurs
    """
    try:
        # Exchange code for GitHub access token
        github_token = await auth_service.exchange_code_for_token(code)

        # Fetch GitHub user profile
        github_user = await auth_service.fetch_github_user(github_token)

        # Create or update user in database
        user = await auth_service.create_or_update_user(github_user, github_token)

        # Generate JWT tokens
        tokens = await auth_service.generate_jwt_tokens(user)

        return TokenResponse(**tokens)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed. Please try again.",
        ) from e


@router.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> RefreshTokenResponse:
    """
    Issue new access token using refresh token.

    This endpoint validates the refresh token and issues a new access token
    without requiring the user to re-authenticate.

    Request Body:
        refresh_token: JWT refresh token

    Returns:
        RefreshTokenResponse with new access_token, token_type, expires_in

    Raises:
        HTTPException: 401 if refresh token is invalid, expired, or revoked
    """
    try:
        tokens = await auth_service.refresh_access_token(request.refresh_token)
        return RefreshTokenResponse(**tokens)

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        ) from e


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    request: LogoutRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> None:
    """
    Logout user by revoking refresh token.

    This endpoint invalidates the refresh token, preventing it from being
    used to obtain new access tokens. The access token will remain valid
    until it expires (15 minutes).

    Request Body:
        refresh_token: JWT refresh token to revoke

    Returns:
        204 No Content on success

    Raises:
        HTTPException: 401 if refresh token is invalid or not found
    """
    try:
        await auth_service.revoke_refresh_token(request.refresh_token)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
        ) from e
