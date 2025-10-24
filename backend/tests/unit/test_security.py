"""Unit tests for security module (JWT token creation and verification)."""

import uuid

import pytest

from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_token,
    verify_token,
)


def test_create_and_verify_access_token():
    """Test creating and verifying JWT access token."""
    user_id = uuid.uuid4()
    token = create_access_token(user_id)

    # Token should be a non-empty string
    assert isinstance(token, str)
    assert len(token) > 0

    # Verify token should return the same user_id
    verified_id = verify_token(token, expected_type="access")
    assert verified_id == user_id


def test_create_and_verify_refresh_token():
    """Test creating and verifying JWT refresh token."""
    user_id = uuid.uuid4()
    token = create_refresh_token(user_id)

    # Token should be a non-empty string
    assert isinstance(token, str)
    assert len(token) > 0

    # Verify token should return the same user_id
    verified_id = verify_token(token, expected_type="refresh")
    assert verified_id == user_id


def test_verify_token_wrong_type():
    """Test verifying token with wrong expected type fails."""
    user_id = uuid.uuid4()
    access_token = create_access_token(user_id)

    # Verifying access token as refresh should fail
    with pytest.raises(ValueError, match="Invalid token type"):
        verify_token(access_token, expected_type="refresh")


def test_verify_invalid_token():
    """Test verifying invalid token fails."""
    with pytest.raises(ValueError, match="Invalid token"):
        verify_token("invalid.token.here", expected_type="access")


def test_hash_token():
    """Test token hashing produces consistent results."""
    token = "test_token_12345"

    hash1 = hash_token(token)
    hash2 = hash_token(token)

    # Same token should produce same hash
    assert hash1 == hash2

    # Hash should be hex string of length 64 (SHA-256)
    assert len(hash1) == 64
    assert all(c in "0123456789abcdef" for c in hash1)


def test_access_token_with_correlation_id():
    """Test creating access token with correlation ID."""
    user_id = uuid.uuid4()
    correlation_id = "test-correlation-123"

    token = create_access_token(user_id, correlation_id)

    # Token should still verify correctly
    verified_id = verify_token(token, expected_type="access")
    assert verified_id == user_id
