"""Authentication service for GitHub OAuth and JWT token management."""

from datetime import UTC, datetime, timedelta
from typing import Any

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decrypt_github_token,
    encrypt_github_token,
    hash_token,
    verify_token,
)
from app.models.refresh_token import RefreshToken
from app.models.user import User


class AuthService:
    """Service for handling authentication operations."""

    def __init__(self, db: AsyncSession):
        """
        Initialize AuthService.

        Args:
            db: Async database session
        """
        self.db = db

    async def exchange_code_for_token(self, code: str) -> str:
        """
        Exchange OAuth authorization code for GitHub access token.

        Args:
            code: OAuth authorization code from GitHub callback

        Returns:
            GitHub access token

        Raises:
            httpx.HTTPStatusError: If GitHub API returns error response
            ValueError: If access token not found in response
        """
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "https://github.com/login/oauth/access_token",
                headers={"Accept": "application/json"},
                data={
                    "client_id": settings.GITHUB_CLIENT_ID,
                    "client_secret": settings.GITHUB_CLIENT_SECRET,
                    "code": code,
                },
            )
            response.raise_for_status()
            data = response.json()

            if "access_token" not in data:
                raise ValueError(
                    f"GitHub OAuth error: {data.get('error_description', 'Unknown error')}"
                )

            return data["access_token"]

    async def fetch_github_user(self, access_token: str) -> dict[str, Any]:
        """
        Fetch user profile from GitHub API.

        Args:
            access_token: GitHub access token

        Returns:
            GitHub user profile data

        Raises:
            httpx.HTTPStatusError: If GitHub API returns error response
        """
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                "https://api.github.com/user",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Accept": "application/vnd.github.v3+json",
                },
            )
            response.raise_for_status()
            return response.json()

    async def create_or_update_user(self, github_user: dict[str, Any], access_token: str) -> User:
        """
        Create or update user from GitHub profile.

        Args:
            github_user: GitHub user profile data
            access_token: GitHub access token

        Returns:
            User model instance

        Raises:
            ValueError: If required fields missing from GitHub profile
        """
        github_id = github_user.get("id")
        if not github_id:
            raise ValueError("GitHub user ID not found in profile")

        # Check if user exists by github_id
        result = await self.db.execute(select(User).where(User.github_id == github_id))
        user = result.scalar_one_or_none()

        # Encrypt GitHub access token before storing
        encrypted_token = encrypt_github_token(access_token)

        if user:
            # Update existing user
            user.username = github_user.get("login", user.username)
            user.email = github_user.get("email") or user.email
            user.avatar_url = github_user.get("avatar_url")
            user.github_access_token = encrypted_token
        else:
            # Create new user
            email = github_user.get("email")
            if not email:
                # If email is private, use a placeholder
                email = f"{github_user.get('login')}@users.noreply.github.com"

            user = User(
                github_id=github_id,
                username=github_user.get("login", f"user_{github_id}"),
                email=email,
                avatar_url=github_user.get("avatar_url"),
                github_access_token=encrypted_token,
            )
            self.db.add(user)

        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def generate_jwt_tokens(
        self, user: User, correlation_id: str | None = None
    ) -> dict[str, Any]:
        """
        Generate access and refresh JWT tokens for user.

        Args:
            user: User model instance
            correlation_id: Optional correlation ID for request tracing

        Returns:
            Dictionary with access_token, refresh_token, token_type, and expires_in
        """
        access_token = create_access_token(user.id, correlation_id)
        refresh_token = create_refresh_token(user.id)

        # Store refresh token in database
        refresh_token_record = RefreshToken(
            user_id=user.id,
            token_hash=hash_token(refresh_token),
            expires_at=datetime.now(UTC) + timedelta(days=7),
            revoked=False,
        )
        self.db.add(refresh_token_record)
        await self.db.commit()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": 900,  # 15 minutes in seconds
        }

    async def verify_access_token(self, token: str) -> User:
        """
        Verify access token and return user.

        Args:
            token: JWT access token

        Returns:
            User model instance

        Raises:
            ValueError: If token is invalid, expired, or user not found
        """
        user_id = verify_token(token, expected_type="access")

        result = await self.db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()

        if not user:
            raise ValueError("User not found")

        return user

    async def refresh_access_token(self, refresh_token: str) -> dict[str, Any]:
        """
        Issue new access token using refresh token.

        Args:
            refresh_token: JWT refresh token

        Returns:
            Dictionary with new access_token, token_type, and expires_in

        Raises:
            ValueError: If refresh token is invalid, expired, revoked, or not found
        """
        # Verify refresh token
        user_id = verify_token(refresh_token, expected_type="refresh")

        # Check if refresh token exists in database and is not revoked
        token_hash_value = hash_token(refresh_token)
        result = await self.db.execute(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash_value,
                RefreshToken.user_id == user_id,
                RefreshToken.revoked == False,  # noqa: E712
            )
        )
        refresh_token_record = result.scalar_one_or_none()

        if not refresh_token_record:
            raise ValueError("Refresh token not found or has been revoked")

        # Check if refresh token is expired
        if refresh_token_record.expires_at < datetime.now(UTC):
            raise ValueError("Refresh token expired")

        # Generate new access token
        access_token = create_access_token(user_id)

        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": 900,  # 15 minutes in seconds
        }

    async def revoke_refresh_token(self, refresh_token: str) -> None:
        """
        Revoke (invalidate) refresh token for logout.

        Args:
            refresh_token: JWT refresh token to revoke

        Raises:
            ValueError: If refresh token is invalid or not found
        """
        # Verify refresh token structure
        user_id = verify_token(refresh_token, expected_type="refresh")

        # Find and revoke token in database
        token_hash_value = hash_token(refresh_token)
        result = await self.db.execute(
            select(RefreshToken).where(
                RefreshToken.token_hash == token_hash_value,
                RefreshToken.user_id == user_id,
            )
        )
        refresh_token_record = result.scalar_one_or_none()

        if not refresh_token_record:
            raise ValueError("Refresh token not found")

        refresh_token_record.revoked = True
        await self.db.commit()

    async def get_decrypted_github_token(self, user: User) -> str | None:
        """
        Get decrypted GitHub access token for user.

        Args:
            user: User model instance

        Returns:
            Decrypted GitHub access token or None if not available
        """
        if not user.github_access_token:
            return None

        return decrypt_github_token(user.github_access_token)
