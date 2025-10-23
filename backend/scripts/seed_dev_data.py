"""Seed development data script for local testing."""

import asyncio
import uuid

from sqlalchemy import select

from app.core.database import AsyncSessionLocal
from app.models.board import Board
from app.models.card import Card, PriorityEnum
from app.models.user import User
from app.models.workspace import Workspace
from app.models.workspace_member import RoleEnum, WorkspaceMember


async def seed_data() -> None:
    """Seed the database with development test data."""
    async with AsyncSessionLocal() as session:
        # Check if data already exists (idempotent)
        result = await session.execute(select(User))
        existing_users = result.scalars().all()

        if len(existing_users) > 0:
            print("✅ Database already contains data. Skipping seed...")
            return

        print("🌱 Seeding development data...")

        # Create test users
        user1 = User(
            github_id=12345,
            username="alice",
            email="user1@github.com",
            avatar_url="https://github.com/alice.png",
            github_access_token="fake_token_alice",
        )
        user2 = User(
            github_id=67890,
            username="bob",
            email="user2@github.com",
            avatar_url="https://github.com/bob.png",
            github_access_token="fake_token_bob",
        )
        session.add_all([user1, user2])
        await session.flush()
        print(f"   👤 Created users: {user1.username}, {user2.username}")

        # Create workspace
        workspace = Workspace(
            name="Test Workspace",
            created_by=user1.id,
        )
        session.add(workspace)
        await session.flush()
        print(f"   🏢 Created workspace: {workspace.name}")

        # Add workspace members
        member1 = WorkspaceMember(
            user_id=user1.id,
            workspace_id=workspace.id,
            role=RoleEnum.ADMIN,
        )
        member2 = WorkspaceMember(
            user_id=user2.id,
            workspace_id=workspace.id,
            role=RoleEnum.MEMBER,
        )
        session.add_all([member1, member2])
        print(f"   👥 Added members: {user1.username} (admin), {user2.username} (member)")

        # Create board with default columns
        column_todo = str(uuid.uuid4())
        column_in_progress = str(uuid.uuid4())
        column_in_review = str(uuid.uuid4())
        column_done = str(uuid.uuid4())

        board = Board(
            workspace_id=workspace.id,
            name="Sprint Board",
            columns=[
                {"id": column_todo, "name": "To Do", "position": 0},
                {"id": column_in_progress, "name": "In Progress", "position": 1},
                {"id": column_in_review, "name": "In Review", "position": 2},
                {"id": column_done, "name": "Done", "position": 3},
            ],
        )
        session.add(board)
        await session.flush()
        print(f"   📋 Created board: {board.name} with 4 columns")

        # Create test cards distributed across columns
        cards = [
            Card(
                board_id=board.id,
                column_id=uuid.UUID(column_todo),
                title="Setup development environment",
                description="Install all dependencies and configure local environment",
                priority=PriorityEnum.HIGH,
                position=0,
                created_by=user1.id,
            ),
            Card(
                board_id=board.id,
                column_id=uuid.UUID(column_todo),
                title="Design database schema",
                description="Create ERD and define all tables and relationships",
                priority=PriorityEnum.MEDIUM,
                position=1,
                created_by=user1.id,
            ),
            Card(
                board_id=board.id,
                column_id=uuid.UUID(column_in_progress),
                title="Implement authentication",
                description="Add GitHub OAuth integration for user login",
                priority=PriorityEnum.URGENT,
                position=0,
                created_by=user2.id,
            ),
            Card(
                board_id=board.id,
                column_id=uuid.UUID(column_in_review),
                title="Create board view UI",
                description="Build drag-and-drop Kanban board interface",
                priority=PriorityEnum.MEDIUM,
                position=0,
                created_by=user1.id,
            ),
            Card(
                board_id=board.id,
                column_id=uuid.UUID(column_done),
                title="Write project README",
                description="Document installation and usage instructions",
                priority=PriorityEnum.LOW,
                position=0,
                created_by=user2.id,
            ),
        ]
        session.add_all(cards)
        print(f"   🎴 Created {len(cards)} test cards across columns")

        # Commit all changes
        await session.commit()
        print("✅ Database seeded successfully!")


def main() -> None:
    """Main entry point for the seed script."""
    asyncio.run(seed_data())


if __name__ == "__main__":
    main()
