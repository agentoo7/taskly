"""Card API endpoints for managing cards and their metadata."""

from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.card import CardCreate, CardDetailResponse, CardResponse, CardUpdate
from app.services.card_service import CardService

router = APIRouter(prefix="/api", tags=["cards"])


@router.post(
    "/boards/{board_id}/cards",
    response_model=CardResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_card(
    board_id: UUID,
    data: CardCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CardResponse:
    """
    Create new card in board column.

    Args:
        board_id: UUID of board to create card in
        data: Card creation data (title, column_id)
        current_user: Current authenticated user
        db: Database session

    Returns:
        Created card at position 0

    Raises:
        HTTPException: 401 if not authenticated, 403 if not workspace member,
                      400 if column doesn't exist, 404 if board not found
    """
    service = CardService(db)
    card = await service.create_card(
        board_id=board_id,
        column_id=data.column_id,
        title=data.title,
        user_id=current_user.id,
    )
    return CardResponse.model_validate(card)


@router.get("/boards/{board_id}/cards", response_model=list[CardResponse])
async def list_board_cards(
    board_id: UUID,
    column_id: UUID | None = Query(default=None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[CardResponse]:
    """
    List all cards in board, optionally filtered by column.

    Args:
        board_id: UUID of board
        column_id: Optional UUID to filter by column
        current_user: Current authenticated user
        db: Database session

    Returns:
        List of cards ordered by position ascending

    Raises:
        HTTPException: 401 if not authenticated, 403 if not workspace member,
                      404 if board not found
    """
    service = CardService(db)
    cards = await service.get_board_cards(
        board_id=board_id, user_id=current_user.id, column_id=column_id
    )
    return [CardResponse.model_validate(c) for c in cards]


@router.get("/cards/{card_id}", response_model=CardDetailResponse)
async def get_card(
    card_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CardDetailResponse:
    """
    Get card details with all metadata.

    Args:
        card_id: UUID of card
        current_user: Current authenticated user
        db: Database session

    Returns:
        Card with full details

    Raises:
        HTTPException: 401 if not authenticated, 403 if not workspace member,
                      404 if card not found
    """
    service = CardService(db)
    card = await service.get_card_by_id(card_id=card_id, user_id=current_user.id)
    return CardDetailResponse.model_validate(card)


@router.patch("/cards/{card_id}", response_model=CardResponse)
async def update_card(
    card_id: UUID,
    data: CardUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> CardResponse:
    """
    Update card properties.

    Args:
        card_id: UUID of card to update
        data: Update data (title, description, priority, due_date, story_points)
        current_user: Current authenticated user
        db: Database session

    Returns:
        Updated card

    Raises:
        HTTPException: 401 if not authenticated, 403 if not workspace member,
                      404 if card not found, 422 if validation fails
    """
    service = CardService(db)
    # Filter out None values (don't update fields not provided)
    updates = {k: v for k, v in data.model_dump().items() if v is not None}
    card = await service.update_card(
        card_id=card_id, user_id=current_user.id, updates=updates
    )
    return CardResponse.model_validate(card)


@router.delete("/cards/{card_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_card(
    card_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    """
    Delete card and reorder remaining cards in column.

    Args:
        card_id: UUID of card to delete
        current_user: Current authenticated user
        db: Database session

    Raises:
        HTTPException: 401 if not authenticated, 403 if not workspace member,
                      404 if card not found
    """
    service = CardService(db)
    await service.delete_card(card_id=card_id, user_id=current_user.id)
