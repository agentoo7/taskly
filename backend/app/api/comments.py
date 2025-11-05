"""API endpoints for card comments."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.notification import Notification, NotificationType
from app.models.user import User
from app.repositories.comment_repository import CommentRepository
from app.schemas.comment import CommentCreate, CommentListResponse, CommentResponse, CommentUpdate
from app.services.comment_service import CommentService
from app.websockets.manager import manager

router = APIRouter()


@router.get("/cards/{card_id}/comments", response_model=CommentListResponse)
async def list_card_comments(
    card_id: UUID,
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of items to return"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CommentListResponse:
    """List comments for a card with pagination."""
    repo = CommentRepository(db)
    comments, total = await repo.get_by_card(card_id, offset=offset, limit=limit)

    return CommentListResponse(
        items=[CommentResponse.model_validate(c) for c in comments],
        total=total,
        offset=offset,
        limit=limit,
    )


@router.post("/cards/{card_id}/comments", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
async def create_comment(
    card_id: UUID,
    data: CommentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CommentResponse:
    """Create a new comment on a card."""
    # Use comment service to handle mentions and create comment
    comment_service = CommentService(db)
    comment, mentioned_usernames = await comment_service.create_comment(
        card_id=card_id,
        user_id=current_user.id,
        text=data.text
    )

    # Create notifications for mentioned users
    if mentioned_usernames:
        # Fetch users by username
        stmt = select(User).where(User.username.in_(mentioned_usernames))
        result = await db.execute(stmt)
        mentioned_users = result.scalars().all()

        # Create notification for each mentioned user (except the author)
        for mentioned_user in mentioned_users:
            if mentioned_user.id != current_user.id:
                notification = Notification(
                    user_id=mentioned_user.id,
                    type=NotificationType.COMMENT_MENTION,
                    card_id=card_id,
                    comment_id=comment.id,
                    title=f"@{current_user.username} mentioned you",
                    message=f"{comment.text[:100]}..." if len(comment.text) > 100 else comment.text
                )
                db.add(notification)

    await db.commit()

    # Refresh comment with eagerly loaded relationships
    from app.models.card import Card
    from app.models.card_comment import CardComment

    stmt = select(CardComment).where(CardComment.id == comment.id).options(selectinload(CardComment.author))
    result = await db.execute(stmt)
    comment = result.scalar_one()

    # Get workspace_id through board relationship for WebSocket broadcasting
    card_stmt = select(Card).options(selectinload(Card.board)).where(Card.id == card_id)
    card_result = await db.execute(card_stmt)
    card = card_result.scalar_one_or_none()

    # Broadcast WebSocket event to workspace (frontend filters by card_id)
    if card and card.board:
        await manager.broadcast_to_workspace(
            workspace_id=str(card.board.workspace_id),
            message={
                "event": "comment_created",
                "data": {
                    "id": str(comment.id),
                    "card_id": str(comment.card_id),
                    "author": {
                        "id": str(comment.author.id),
                        "username": comment.author.username,
                        "avatar_url": comment.author.avatar_url,
                    },
                    "text": comment.text,
                    "created_at": comment.created_at.isoformat(),
                    "updated_at": comment.updated_at.isoformat(),
                },
            },
            exclude_user_id=str(current_user.id),
        )

    return CommentResponse.model_validate(comment)


@router.patch("/comments/{comment_id}", response_model=CommentResponse)
async def update_comment(
    comment_id: UUID,
    data: CommentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CommentResponse:
    """Update a comment (author only)."""
    repo = CommentRepository(db)
    comment = await repo.get_by_id(comment_id)

    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You can only edit your own comments"
        )

    updated_comment = await repo.update(comment_id, data.text)
    await db.commit()

    return CommentResponse.model_validate(updated_comment)


@router.delete("/comments/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_comment(
    comment_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    """Delete a comment (author only)."""
    repo = CommentRepository(db)
    comment = await repo.get_by_id(comment_id)

    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comment not found")

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="You can only delete your own comments"
        )

    await repo.soft_delete(comment_id)
    await db.commit()
