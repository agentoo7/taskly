"""Integration tests for authentication endpoints."""

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.models.refresh_token import RefreshToken
from app.models.user import User


@pytest.mark.asyncio
async def test_health_check_no_auth(client: AsyncClient):
    """Test that health check endpoint does not require authentication."""
    response = await client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
@patch("app.services.auth_service.httpx.AsyncClient")
async def test_github_callback_success(
    mock_httpx, client: AsyncClient, db_session
):
    """Test successful GitHub OAuth callback flow."""
    # Mock GitHub OAuth responses
    mock_client_instance = AsyncMock()

    # Mock token exchange response
    mock_token_response = AsyncMock()
    mock_token_response.json.return_value = {
        "access_token": "gho_test_token_12345"
    }
    mock_token_response.raise_for_status = AsyncMock()

    # Mock user profile response
    mock_user_response = AsyncMock()
    mock_user_response.json.return_value = {
        "id": 12345678,
        "login": "testuser",
        "email": "test@example.com",
        "avatar_url": "https://avatars.githubusercontent.com/u/12345678",
    }
    mock_user_response.raise_for_status = AsyncMock()

    # Configure mock client
    mock_client_instance.post.return_value = mock_token_response
    mock_client_instance.get.return_value = mock_user_response
    mock_client_instance.__aenter__.return_value = mock_client_instance
    mock_client_instance.__aexit__.return_value = AsyncMock()

    mock_httpx.return_value = mock_client_instance

    # Make request to callback endpoint
    response = await client.get("/auth/github/callback?code=test_code_123")

    assert response.status_code == 200
    data = response.json()

    # Verify response structure
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"
    assert data["expires_in"] == 900

    # Verify user was created in database
    result = await db_session.execute(
        select(User).where(User.github_id == 12345678)
    )
    user = result.scalar_one_or_none()
    assert user is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"

    # Verify refresh token was stored
    result = await db_session.execute(
        select(RefreshToken).where(RefreshToken.user_id == user.id)
    )
    refresh_token_record = result.scalar_one_or_none()
    assert refresh_token_record is not None
    assert refresh_token_record.revoked is False


@pytest.mark.asyncio
async def test_github_callback_missing_code(client: AsyncClient):
    """Test GitHub callback with missing code parameter."""
    response = await client.get("/auth/github/callback")
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_get_me_without_auth(client: AsyncClient):
    """Test /api/me endpoint without authentication returns 401."""
    response = await client.get("/api/me")
    assert response.status_code == 401


@pytest.mark.asyncio
@patch("app.services.auth_service.httpx.AsyncClient")
async def test_get_me_with_auth(mock_httpx, client: AsyncClient, db_session):
    """Test /api/me endpoint with valid authentication."""
    # Create test user and tokens
    mock_client_instance = AsyncMock()
    mock_token_response = AsyncMock()
    mock_token_response.json.return_value = {
        "access_token": "gho_test_token_67890"
    }
    mock_token_response.raise_for_status = AsyncMock()

    mock_user_response = AsyncMock()
    mock_user_response.json.return_value = {
        "id": 87654321,
        "login": "authuser",
        "email": "auth@example.com",
        "avatar_url": "https://avatars.githubusercontent.com/u/87654321",
    }
    mock_user_response.raise_for_status = AsyncMock()

    mock_client_instance.post.return_value = mock_token_response
    mock_client_instance.get.return_value = mock_user_response
    mock_client_instance.__aenter__.return_value = mock_client_instance
    mock_client_instance.__aexit__.return_value = AsyncMock()
    mock_httpx.return_value = mock_client_instance

    # First, authenticate to get token
    auth_response = await client.get("/auth/github/callback?code=test_code_456")
    assert auth_response.status_code == 200
    auth_data = auth_response.json()
    access_token = auth_data["access_token"]

    # Now call /api/me with the token
    response = await client.get(
        "/api/me", headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "authuser"
    assert data["email"] == "auth@example.com"
    assert data["github_id"] == 87654321


@pytest.mark.asyncio
async def test_logout(client: AsyncClient):
    """Test logout endpoint revokes refresh token."""
    # This test would need to first authenticate, then logout
    # For now, test that endpoint exists and handles invalid token
    response = await client.post(
        "/auth/logout", json={"refresh_token": "invalid_token"}
    )
    # Should return 401 for invalid token
    assert response.status_code == 401
