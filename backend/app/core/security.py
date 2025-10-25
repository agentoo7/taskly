"""Security utilities for JWT token generation and validation."""

import hashlib
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from app.core.config import settings


def create_access_token(user_id: uuid.UUID, correlation_id: str | None = None) -> str:
    """
    Create JWT access token with 15 minute expiration.

    Args:
        user_id: User's UUID
        correlation_id: Optional correlation ID for request tracing

    Returns:
        Encoded JWT access token
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=15)

    payload: dict[str, Any] = {
        "sub": str(user_id),
        "type": "access",
        "exp": expire,
        "iat": now,
    }

    if correlation_id:
        payload["correlation_id"] = correlation_id

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(user_id: uuid.UUID) -> str:
    """
    Create JWT refresh token with 7 day expiration.

    Args:
        user_id: User's UUID

    Returns:
        Encoded JWT refresh token
    """
    now = datetime.now(timezone.utc)
    expire = now + timedelta(days=7)

    payload: dict[str, Any] = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": expire,
        "iat": now,
    }

    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_jwt_token(token: str) -> dict[str, Any]:
    """
    Decode JWT token and return payload without verification of type.

    Args:
        token: JWT token to decode

    Returns:
        Token payload dictionary

    Raises:
        ValueError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError as e:
        raise ValueError("Token expired") from e
    except jwt.InvalidTokenError as e:
        raise ValueError("Invalid token") from e


def verify_token(token: str, expected_type: str = "access") -> uuid.UUID:
    """
    Verify JWT token and return user_id.

    Args:
        token: JWT token to verify
        expected_type: Expected token type ("access" or "refresh")

    Returns:
        User's UUID from token payload

    Raises:
        ValueError: If token is invalid, expired, or wrong type
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

        if payload.get("type") != expected_type:
            raise ValueError(f"Invalid token type. Expected {expected_type}")

        user_id = uuid.UUID(payload["sub"])
        return user_id

    except jwt.ExpiredSignatureError as e:
        raise ValueError("Token expired") from e
    except jwt.InvalidTokenError as e:
        raise ValueError("Invalid token") from e


def hash_token(token: str) -> str:
    """
    Hash token for secure storage.

    Args:
        token: Token to hash

    Returns:
        SHA-256 hash of token
    """
    return hashlib.sha256(token.encode()).hexdigest()


def encrypt_github_token(token: str) -> str:
    """
    Encrypt GitHub access token before storing in database.

    TODO: Implement proper AES encryption for production.
    For development, returns token as-is.

    Args:
        token: GitHub access token

    Returns:
        Encrypted token (currently plaintext)
    """
    # TODO: Implement AES encryption using cryptography library
    # from cryptography.fernet import Fernet
    # cipher = Fernet(settings.ENCRYPTION_KEY)
    # return cipher.encrypt(token.encode()).decode()
    return token


def decrypt_github_token(encrypted_token: str) -> str:
    """
    Decrypt GitHub access token from database.

    TODO: Implement proper AES decryption for production.
    For development, returns token as-is.

    Args:
        encrypted_token: Encrypted GitHub access token

    Returns:
        Decrypted token (currently plaintext)
    """
    # TODO: Implement AES decryption using cryptography library
    # from cryptography.fernet import Fernet
    # cipher = Fernet(settings.ENCRYPTION_KEY)
    # return cipher.decrypt(encrypted_token.encode()).decode()
    return encrypted_token
