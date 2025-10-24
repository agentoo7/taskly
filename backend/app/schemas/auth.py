"""Pydantic schemas for authentication endpoints."""

import uuid

from pydantic import BaseModel, EmailStr, Field


class TokenResponse(BaseModel):
    """Response schema for token issuance."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="JWT refresh token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration in seconds")


class RefreshTokenRequest(BaseModel):
    """Request schema for token refresh."""

    refresh_token: str = Field(..., description="JWT refresh token")


class RefreshTokenResponse(BaseModel):
    """Response schema for token refresh."""

    access_token: str = Field(..., description="New JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Access token expiration in seconds")


class LogoutRequest(BaseModel):
    """Request schema for logout."""

    refresh_token: str = Field(..., description="JWT refresh token to revoke")


class UserProfile(BaseModel):
    """User profile schema for /api/me endpoint."""

    id: uuid.UUID = Field(..., description="User's UUID")
    username: str = Field(..., description="GitHub username")
    email: EmailStr = Field(..., description="User's email")
    avatar_url: str | None = Field(None, description="GitHub avatar URL")
    github_id: int = Field(..., description="GitHub user ID")

    class Config:
        """Pydantic config."""

        from_attributes = True
