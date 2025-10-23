"""Base repository with common CRUD operations."""

from typing import Generic, Optional, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base repository class with common CRUD operations."""

    def __init__(self, model: type[ModelType], session: AsyncSession):
        """Initialize repository with model and database session.

        Args:
            model: SQLAlchemy model class
            session: Async database session
        """
        self.model = model
        self.session = session

    async def get_by_id(self, id: UUID) -> Optional[ModelType]:
        """Get a record by its ID.

        Args:
            id: UUID of the record

        Returns:
            Model instance or None if not found
        """
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)  # type: ignore[attr-defined]
        )
        return result.scalar_one_or_none()

    async def get_all(self, skip: int = 0, limit: int = 100) -> list[ModelType]:
        """Get all records with pagination.

        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return

        Returns:
            List of model instances
        """
        result = await self.session.execute(select(self.model).offset(skip).limit(limit))
        return list(result.scalars().all())

    async def create(self, obj: ModelType) -> ModelType:
        """Create a new record.

        Args:
            obj: Model instance to create

        Returns:
            Created model instance with populated fields
        """
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def update(self, obj: ModelType) -> ModelType:
        """Update an existing record.

        Args:
            obj: Model instance with updated fields

        Returns:
            Updated model instance
        """
        await self.session.flush()
        await self.session.refresh(obj)
        return obj

    async def delete(self, obj: ModelType) -> None:
        """Delete a record.

        Args:
            obj: Model instance to delete
        """
        await self.session.delete(obj)
        await self.session.flush()
