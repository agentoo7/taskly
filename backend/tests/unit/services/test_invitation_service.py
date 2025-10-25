"""Unit tests for InvitationService."""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.invitation_service import InvitationService


@pytest.fixture
async def invitation_service(db_session: AsyncSession) -> InvitationService:
    """Create an InvitationService instance with test database."""
    return InvitationService(db_session)


class TestTokenGeneration:
    """Tests for token generation."""

    @pytest.mark.asyncio
    async def test_generate_token_creates_unique_tokens(
        self, invitation_service: InvitationService
    ):
        """Test that generated tokens are unique."""
        token1 = invitation_service.generate_invitation_token()
        token2 = invitation_service.generate_invitation_token()

        assert token1 != token2
        assert len(token1) == 64  # 32 bytes = 64 hex characters
        assert len(token2) == 64

    @pytest.mark.asyncio
    async def test_generate_token_format(self, invitation_service: InvitationService):
        """Test that generated token has correct format (hexadecimal)."""
        token = invitation_service.generate_invitation_token()

        # Should be hexadecimal
        assert all(c in "0123456789abcdef" for c in token)
        assert len(token) == 64
