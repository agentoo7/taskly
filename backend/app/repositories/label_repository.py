"""Label repository for database operations."""

from typing import Sequence
from uuid import UUID

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.card_label import CardLabel
from app.models.workspace_label import WorkspaceLabel


class LabelRepository:
    """Repository for label-related database operations."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize label repository."""
        self.session = session

    async def create_label(
        self, workspace_id: UUID, name: str, color: str
    ) -> WorkspaceLabel:
        """Create a new workspace label."""
        label = WorkspaceLabel(workspace_id=workspace_id, name=name, color=color)
        self.session.add(label)
        await self.session.flush()
        await self.session.refresh(label)
        return label

    async def get_label_by_id(self, label_id: UUID) -> WorkspaceLabel | None:
        """Get label by ID."""
        result = await self.session.execute(
            select(WorkspaceLabel).where(WorkspaceLabel.id == label_id)
        )
        return result.scalar_one_or_none()

    async def get_workspace_labels(self, workspace_id: UUID) -> Sequence[WorkspaceLabel]:
        """Get all labels for a workspace."""
        result = await self.session.execute(
            select(WorkspaceLabel)
            .where(WorkspaceLabel.workspace_id == workspace_id)
            .order_by(WorkspaceLabel.created_at.desc())
        )
        return result.scalars().all()

    async def update_label(
        self, label_id: UUID, name: str | None = None, color: str | None = None
    ) -> WorkspaceLabel | None:
        """Update label name and/or color."""
        label = await self.get_label_by_id(label_id)
        if not label:
            return None

        if name is not None:
            label.name = name
        if color is not None:
            label.color = color

        await self.session.flush()
        await self.session.refresh(label)
        return label

    async def delete_label(self, label_id: UUID) -> bool:
        """Delete a label and all its card associations."""
        label = await self.get_label_by_id(label_id)
        if not label:
            return False

        await self.session.delete(label)
        await self.session.flush()
        return True

    async def count_cards_with_label(self, label_id: UUID) -> int:
        """Count how many cards use this label."""
        result = await self.session.execute(
            select(func.count(CardLabel.card_id)).where(CardLabel.label_id == label_id)
        )
        return result.scalar() or 0

    async def add_label_to_card(self, card_id: UUID, label_id: UUID) -> CardLabel:
        """Add a label to a card."""
        # Check if already exists
        result = await self.session.execute(
            select(CardLabel).where(
                CardLabel.card_id == card_id,
                CardLabel.label_id == label_id
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            raise ValueError("Label already added to this card")

        card_label = CardLabel(card_id=card_id, label_id=label_id)
        self.session.add(card_label)
        await self.session.flush()
        return card_label

    async def remove_label_from_card(self, card_id: UUID, label_id: UUID) -> bool:
        """Remove a label from a card."""
        result = await self.session.execute(
            delete(CardLabel).where(
                CardLabel.card_id == card_id, CardLabel.label_id == label_id
            )
        )
        await self.session.flush()
        return result.rowcount > 0

    async def get_card_labels(self, card_id: UUID) -> Sequence[WorkspaceLabel]:
        """Get all labels for a card."""
        result = await self.session.execute(
            select(WorkspaceLabel)
            .join(CardLabel, CardLabel.label_id == WorkspaceLabel.id)
            .where(CardLabel.card_id == card_id)
        )
        return result.scalars().all()
