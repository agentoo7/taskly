"""Label service for business logic."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.label_repository import LabelRepository
from app.schemas.label import LabelCreate, LabelResponse, LabelUpdate
from app.services.workspace_service import WorkspaceService


class LabelService:
    """Service for label business logic."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize label service."""
        self.label_repo = LabelRepository(session)
        self.workspace_service = WorkspaceService(session)
        self.session = session

    async def create_label(
        self, workspace_id: UUID, label_data: LabelCreate, user_id: UUID
    ) -> LabelResponse:
        """Create a new workspace label."""
        # Verify user is workspace member
        is_member = await self.workspace_service.check_workspace_member(workspace_id, user_id)
        if not is_member:
            raise PermissionError("User is not a member of this workspace")

        label = await self.label_repo.create_label(
            workspace_id=workspace_id, name=label_data.name, color=label_data.color
        )
        return LabelResponse.model_validate(label)

    async def get_workspace_labels(self, workspace_id: UUID, user_id: UUID) -> list[LabelResponse]:
        """Get all labels for a workspace."""
        # Verify user is workspace member
        is_member = await self.workspace_service.check_workspace_member(workspace_id, user_id)
        if not is_member:
            raise PermissionError("User is not a member of this workspace")

        labels = await self.label_repo.get_workspace_labels(workspace_id)
        return [LabelResponse.model_validate(label) for label in labels]

    async def update_label(
        self, label_id: UUID, label_data: LabelUpdate, user_id: UUID
    ) -> LabelResponse:
        """Update a label's name and/or color."""
        label = await self.label_repo.get_label_by_id(label_id)
        if not label:
            raise ValueError("Label not found")

        # Verify user is workspace member
        is_member = await self.workspace_service.check_workspace_member(
            label.workspace_id, user_id
        )
        if not is_member:
            raise PermissionError("User is not a member of this workspace")

        updated_label = await self.label_repo.update_label(
            label_id=label_id, name=label_data.name, color=label_data.color
        )
        if not updated_label:
            raise ValueError("Label not found")

        return LabelResponse.model_validate(updated_label)

    async def delete_label(self, label_id: UUID, user_id: UUID) -> dict[str, int]:
        """Delete a label and return count of affected cards."""
        label = await self.label_repo.get_label_by_id(label_id)
        if not label:
            raise ValueError("Label not found")

        # Verify user is workspace member
        is_member = await self.workspace_service.check_workspace_member(
            label.workspace_id, user_id
        )
        if not is_member:
            raise PermissionError("User is not a member of this workspace")

        # Count affected cards
        card_count = await self.label_repo.count_cards_with_label(label_id)

        # Delete label (cascade will remove card_labels entries)
        await self.label_repo.delete_label(label_id)
        await self.session.commit()

        return {"cards_affected": card_count}

    async def add_label_to_card(
        self, card_id: UUID, label_id: UUID, user_id: UUID
    ) -> LabelResponse:
        """Add a label to a card."""
        label = await self.label_repo.get_label_by_id(label_id)
        if not label:
            raise ValueError("Label not found")

        # Verify user is workspace member
        is_member = await self.workspace_service.check_workspace_member(
            label.workspace_id, user_id
        )
        if not is_member:
            raise PermissionError("User is not a member of this workspace")

        try:
            await self.label_repo.add_label_to_card(card_id, label_id)
        except ValueError as e:
            # Re-raise as ValueError so API layer can convert to 409
            raise ValueError(str(e))

        return LabelResponse.model_validate(label)

    async def remove_label_from_card(
        self, card_id: UUID, label_id: UUID, user_id: UUID
    ) -> bool:
        """Remove a label from a card."""
        label = await self.label_repo.get_label_by_id(label_id)
        if not label:
            raise ValueError("Label not found")

        # Verify user is workspace member
        is_member = await self.workspace_service.check_workspace_member(
            label.workspace_id, user_id
        )
        if not is_member:
            raise PermissionError("User is not a member of this workspace")

        return await self.label_repo.remove_label_from_card(card_id, label_id)
