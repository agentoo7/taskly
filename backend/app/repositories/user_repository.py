"""User repository for database operations."""

from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository for User model operations."""

    def __init__(self, session: AsyncSession):
        """Initialize UserRepository.

        Args:
            session: Async database session
        """
        super().__init__(User, session)

    async def get_by_github_id(self, github_id: int) -> Optional[User]:
        """Get user by GitHub ID.

        Args:
            github_id: GitHub user ID

        Returns:
            User instance or None if not found
        """
        result = await self.session.execute(select(User).where(User.github_id == github_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """Get user by email.

        Args:
            email: User email address

        Returns:
            User instance or None if not found
        """
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()
