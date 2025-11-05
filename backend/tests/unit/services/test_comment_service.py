"""Unit tests for comment service."""

import pytest
from uuid import uuid4

from app.services.comment_service import CommentService


@pytest.fixture
def comment_service(db_session):
    """Create comment service instance."""
    return CommentService(db_session)


def test_parse_mentions(comment_service):
    """Test mention parsing from comment text."""
    text = "Hey @alice and @bob-smith, check this out! @user_123"
    mentions = comment_service.parse_mentions(text)

    assert len(mentions) == 3
    assert "alice" in mentions
    assert "bob-smith" in mentions
    assert "user_123" in mentions


def test_parse_mentions_empty(comment_service):
    """Test parsing comment with no mentions."""
    text = "This is a comment without mentions"
    mentions = comment_service.parse_mentions(text)

    assert len(mentions) == 0


def test_parse_mentions_duplicates(comment_service):
    """Test parsing handles duplicate mentions."""
    text = "@alice @alice @bob"
    mentions = comment_service.parse_mentions(text)

    # Should return all matches including duplicates (deduplication handled at higher level)
    assert mentions.count("alice") == 2
    assert mentions.count("bob") == 1


@pytest.mark.asyncio
async def test_create_comment(comment_service, db_session):
    """Test creating a comment with mentions."""
    from app.models.card import Card
    from app.models.user import User
    from app.models.board import Board
    from app.models.workspace import Workspace

    # Create test data
    workspace = Workspace(name="Test Workspace")
    db_session.add(workspace)
    await db_session.flush()

    user = User(
        github_id=12345,
        username="testuser",
        email="test@example.com",
    )
    db_session.add(user)
    await db_session.flush()

    board = Board(
        name="Test Board",
        workspace_id=workspace.id,
    )
    db_session.add(board)
    await db_session.flush()

    card = Card(
        title="Test Card",
        board_id=board.id,
        column_id=uuid4(),
        created_by=user.id,
        position=0,
    )
    db_session.add(card)
    await db_session.flush()

    # Create comment with mentions
    text = "Hey @alice, what do you think?"
    comment, mentions = await comment_service.create_comment(
        card_id=card.id, user_id=user.id, text=text
    )

    assert comment.text == text
    assert comment.card_id == card.id
    assert comment.user_id == user.id
    assert "alice" in mentions
    assert comment.comment_metadata.get("mentioned_usernames") == mentions


@pytest.mark.asyncio
async def test_update_comment(comment_service, db_session):
    """Test updating a comment."""
    from app.models.card import Card
    from app.models.user import User
    from app.models.board import Board
    from app.models.workspace import Workspace
    from app.models.card_comment import CardComment

    # Create test data
    workspace = Workspace(name="Test Workspace")
    db_session.add(workspace)
    await db_session.flush()

    user = User(github_id=12345, username="testuser", email="test@example.com")
    db_session.add(user)
    await db_session.flush()

    board = Board(name="Test Board", workspace_id=workspace.id)
    db_session.add(board)
    await db_session.flush()

    card = Card(
        title="Test Card",
        board_id=board.id,
        column_id=uuid4(),
        created_by=user.id,
        position=0,
    )
    db_session.add(card)
    await db_session.flush()

    comment = CardComment(card_id=card.id, user_id=user.id, text="Original text")
    db_session.add(comment)
    await db_session.flush()

    # Update comment
    new_text = "Updated text with @bob"
    updated = await comment_service.update_comment(comment.id, new_text, user.id)

    assert updated is not None
    assert updated.text == new_text
    assert "bob" in updated.comment_metadata.get("mentioned_usernames", [])


@pytest.mark.asyncio
async def test_delete_comment(comment_service, db_session):
    """Test soft deleting a comment."""
    from app.models.card import Card
    from app.models.user import User
    from app.models.board import Board
    from app.models.workspace import Workspace
    from app.models.card_comment import CardComment

    # Create test data
    workspace = Workspace(name="Test Workspace")
    db_session.add(workspace)
    await db_session.flush()

    user = User(github_id=12345, username="testuser", email="test@example.com")
    db_session.add(user)
    await db_session.flush()

    board = Board(name="Test Board", workspace_id=workspace.id)
    db_session.add(board)
    await db_session.flush()

    card = Card(
        title="Test Card",
        board_id=board.id,
        column_id=uuid4(),
        created_by=user.id,
        position=0,
    )
    db_session.add(card)
    await db_session.flush()

    comment = CardComment(card_id=card.id, user_id=user.id, text="Test comment")
    db_session.add(comment)
    await db_session.flush()

    # Delete comment
    result = await comment_service.delete_comment(comment.id, user.id)

    assert result is True

    # Verify soft delete
    await db_session.refresh(comment)
    assert comment.deleted_at is not None
