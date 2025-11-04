"""Assignee service for business logic."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.assignee_repository import AssigneeRepository
from app.repositories.card_repository import CardRepository
from app.schemas.user import UserResponse
from app.services.workspace_service import WorkspaceService


class AssigneeService:
    """Service for assignee business logic."""

    def __init__(self, session: AsyncSession) -> None:
        """Initialize assignee service."""
        self.assignee_repo = AssigneeRepository(session)
        self.card_repo = CardRepository(session)
        self.workspace_service = WorkspaceService(session)
        self.session = session

    async def assign_user_to_card(
        self, card_id: UUID, user_id: UUID, current_user_id: UUID
    ) -> UserResponse:
        """Assign a user to a card."""
        # Get card to verify workspace membership
        card = await self.card_repo.get_with_board(card_id)
        if not card:
            raise ValueError("Card not found")

        # Verify current user is workspace member
        is_member = await self.workspace_service.check_workspace_member(
            card.board.workspace_id, current_user_id
        )
        if not is_member:
            raise PermissionError("User is not a member of this workspace")

        # Verify assignee is workspace member
        is_assignee_member = await self.workspace_service.check_workspace_member(
            card.board.workspace_id, user_id
        )
        if not is_assignee_member:
            raise ValueError("Assignee is not a member of this workspace")

        # Check if already assigned
        is_assigned = await self.assignee_repo.is_user_assigned(card_id, user_id)
        if is_assigned:
            raise ValueError("User is already assigned to this card")

        # Assign user
        await self.assignee_repo.assign_user_to_card(card_id, user_id)

        # Return user info
        assignees = await self.assignee_repo.get_card_assignees(card_id)
        assigned_user = next((u for u in assignees if u.id == user_id), None)
        if not assigned_user:
            raise ValueError("Failed to assign user")

        return UserResponse.model_validate(assigned_user)

    async def unassign_user_from_card(
        self, card_id: UUID, user_id: UUID, current_user_id: UUID
    ) -> bool:
        """Unassign a user from a card."""
        # Get card to verify workspace membership
        card = await self.card_repo.get_with_board(card_id)
        if not card:
            raise ValueError("Card not found")

        # Verify current user is workspace member
        is_member = await self.workspace_service.check_workspace_member(
            card.board.workspace_id, current_user_id
        )
        if not is_member:
            raise PermissionError("User is not a member of this workspace")

        # Unassign user
        return await self.assignee_repo.unassign_user_from_card(card_id, user_id)
