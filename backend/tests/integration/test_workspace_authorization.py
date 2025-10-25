"""Integration tests for workspace authorization boundaries.

Tests verify that permission enforcement works correctly at the HTTP/API layer,
complementing the service layer tests in test_workspace_service.py.

Coverage:
- Admin-only operations (update, delete)
- Member vs non-member access
- Authentication requirements
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.workspace import Workspace
from app.models.workspace_member import RoleEnum, WorkspaceMember
from app.services.auth_service import AuthService


# ============================================================================
# Fixtures
# ============================================================================


@pytest.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Create a standard test user."""
    user = User(
        github_id=111111,
        username="testuser",
        email="testuser@example.com",
        github_access_token="encrypted_token_1",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def admin_user(db_session: AsyncSession) -> User:
    """Create an admin user."""
    user = User(
        github_id=222222,
        username="adminuser",
        email="admin@example.com",
        github_access_token="encrypted_token_2",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def member_user(db_session: AsyncSession) -> User:
    """Create a member (non-admin) user."""
    user = User(
        github_id=333333,
        username="memberuser",
        email="member@example.com",
        github_access_token="encrypted_token_3",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def non_member_user(db_session: AsyncSession) -> User:
    """Create a user who is not a member of any workspace."""
    user = User(
        github_id=444444,
        username="nonmemberuser",
        email="nonmember@example.com",
        github_access_token="encrypted_token_4",
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def test_workspace_with_members(
    db_session: AsyncSession,
    admin_user: User,
    member_user: User,
) -> Workspace:
    """Create a workspace with admin and member users."""
    workspace = Workspace(
        name="Test Workspace",
        created_by=admin_user.id,
    )
    db_session.add(workspace)
    await db_session.flush()

    # Add admin membership
    admin_membership = WorkspaceMember(
        user_id=admin_user.id,
        workspace_id=workspace.id,
        role=RoleEnum.ADMIN,
    )
    # Add member membership
    member_membership = WorkspaceMember(
        user_id=member_user.id,
        workspace_id=workspace.id,
        role=RoleEnum.MEMBER,
    )
    db_session.add_all([admin_membership, member_membership])
    await db_session.commit()
    await db_session.refresh(workspace)
    return workspace


@pytest.fixture
async def admin_token(admin_user: User, db_session: AsyncSession) -> str:
    """Generate JWT access token for admin user."""
    auth_service = AuthService(db_session)
    tokens = await auth_service.generate_jwt_tokens(admin_user)
    return tokens["access_token"]


@pytest.fixture
async def member_token(member_user: User, db_session: AsyncSession) -> str:
    """Generate JWT access token for member user."""
    auth_service = AuthService(db_session)
    tokens = await auth_service.generate_jwt_tokens(member_user)
    return tokens["access_token"]


@pytest.fixture
async def non_member_token(non_member_user: User, db_session: AsyncSession) -> str:
    """Generate JWT access token for non-member user."""
    auth_service = AuthService(db_session)
    tokens = await auth_service.generate_jwt_tokens(non_member_user)
    return tokens["access_token"]


# ============================================================================
# Tests: Admin Operations
# ============================================================================


@pytest.mark.asyncio
async def test_admin_can_update_workspace(
    client: AsyncClient,
    test_workspace_with_members: Workspace,
    admin_token: str,
) -> None:
    """
    Test that admin users can update workspace.

    Given: Admin user with valid JWT token
    When: PATCH /api/workspaces/{id} with new name
    Then: Returns 200 with updated workspace
    """
    response = await client.patch(
        f"/api/workspaces/{test_workspace_with_members.id}",
        json={"name": "Updated Workspace Name"},
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Workspace Name"
    assert data["id"] == str(test_workspace_with_members.id)


@pytest.mark.asyncio
async def test_admin_can_delete_workspace(
    client: AsyncClient,
    test_workspace_with_members: Workspace,
    admin_token: str,
) -> None:
    """
    Test that admin users can delete workspace.

    Given: Admin user with valid JWT token
    When: DELETE /api/workspaces/{id}
    Then: Returns 204 No Content
    """
    response = await client.delete(
        f"/api/workspaces/{test_workspace_with_members.id}",
        headers={"Authorization": f"Bearer {admin_token}"},
    )

    assert response.status_code == 204


# ============================================================================
# Tests: Member Restrictions
# ============================================================================


@pytest.mark.asyncio
async def test_member_cannot_update_workspace(
    client: AsyncClient,
    test_workspace_with_members: Workspace,
    member_token: str,
) -> None:
    """
    Test that non-admin members cannot update workspace.

    Given: Member user (non-admin) with valid JWT token
    When: PATCH /api/workspaces/{id} with new name
    Then: Returns 403 Forbidden
    """
    response = await client.patch(
        f"/api/workspaces/{test_workspace_with_members.id}",
        json={"name": "Hacked Name"},
        headers={"Authorization": f"Bearer {member_token}"},
    )

    assert response.status_code == 403
    data = response.json()
    assert "admin" in data["detail"].lower()


@pytest.mark.asyncio
async def test_member_cannot_delete_workspace(
    client: AsyncClient,
    test_workspace_with_members: Workspace,
    member_token: str,
) -> None:
    """
    Test that non-admin members cannot delete workspace.

    Given: Member user (non-admin) with valid JWT token
    When: DELETE /api/workspaces/{id}
    Then: Returns 403 Forbidden
    """
    response = await client.delete(
        f"/api/workspaces/{test_workspace_with_members.id}",
        headers={"Authorization": f"Bearer {member_token}"},
    )

    assert response.status_code == 403
    data = response.json()
    assert "admin" in data["detail"].lower()


# ============================================================================
# Tests: Non-Member Restrictions
# ============================================================================


@pytest.mark.asyncio
async def test_non_member_cannot_view_workspace(
    client: AsyncClient,
    test_workspace_with_members: Workspace,
    non_member_token: str,
) -> None:
    """
    Test that non-members cannot view workspace details.

    Given: Authenticated user who is NOT a member of workspace
    When: GET /api/workspaces/{id}
    Then: Returns 403 Forbidden
    """
    response = await client.get(
        f"/api/workspaces/{test_workspace_with_members.id}",
        headers={"Authorization": f"Bearer {non_member_token}"},
    )

    assert response.status_code == 403
    data = response.json()
    assert "member" in data["detail"].lower()


@pytest.mark.asyncio
async def test_non_member_cannot_update_workspace(
    client: AsyncClient,
    test_workspace_with_members: Workspace,
    non_member_token: str,
) -> None:
    """
    Test that non-members cannot update workspace.

    Given: Authenticated user who is NOT a member of workspace
    When: PATCH /api/workspaces/{id}
    Then: Returns 403 Forbidden (member check happens before admin check)
    """
    response = await client.patch(
        f"/api/workspaces/{test_workspace_with_members.id}",
        json={"name": "Hacked Name"},
        headers={"Authorization": f"Bearer {non_member_token}"},
    )

    # Should fail at membership check (403) before reaching admin check
    # Note: Currently update doesn't have check_workspace_member dependency,
    # so it will fail at _check_admin instead (which checks membership)
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_non_member_cannot_delete_workspace(
    client: AsyncClient,
    test_workspace_with_members: Workspace,
    non_member_token: str,
) -> None:
    """
    Test that non-members cannot delete workspace.

    Given: Authenticated user who is NOT a member of workspace
    When: DELETE /api/workspaces/{id}
    Then: Returns 403 Forbidden
    """
    response = await client.delete(
        f"/api/workspaces/{test_workspace_with_members.id}",
        headers={"Authorization": f"Bearer {non_member_token}"},
    )

    assert response.status_code == 403


# ============================================================================
# Tests: Authentication Required
# ============================================================================


@pytest.mark.asyncio
async def test_unauthenticated_cannot_list_workspaces(client: AsyncClient) -> None:
    """
    Test that unauthenticated requests to list workspaces return 401.

    Given: No authentication token
    When: GET /api/workspaces
    Then: Returns 401 Unauthorized
    """
    response = await client.get("/api/workspaces")

    assert response.status_code == 401
    data = response.json()
    assert "detail" in data


@pytest.mark.asyncio
async def test_unauthenticated_cannot_create_workspace(client: AsyncClient) -> None:
    """
    Test that unauthenticated requests to create workspace return 401.

    Given: No authentication token
    When: POST /api/workspaces
    Then: Returns 401 Unauthorized
    """
    response = await client.post(
        "/api/workspaces",
        json={"name": "Unauthorized Workspace"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_unauthenticated_cannot_view_workspace(
    client: AsyncClient,
    test_workspace_with_members: Workspace,
) -> None:
    """
    Test that unauthenticated requests to view workspace return 401.

    Given: No authentication token
    When: GET /api/workspaces/{id}
    Then: Returns 401 Unauthorized
    """
    response = await client.get(f"/api/workspaces/{test_workspace_with_members.id}")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_unauthenticated_cannot_update_workspace(
    client: AsyncClient,
    test_workspace_with_members: Workspace,
) -> None:
    """
    Test that unauthenticated requests to update workspace return 401.

    Given: No authentication token
    When: PATCH /api/workspaces/{id}
    Then: Returns 401 Unauthorized
    """
    response = await client.patch(
        f"/api/workspaces/{test_workspace_with_members.id}",
        json={"name": "Hacked Name"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_unauthenticated_cannot_delete_workspace(
    client: AsyncClient,
    test_workspace_with_members: Workspace,
) -> None:
    """
    Test that unauthenticated requests to delete workspace return 401.

    Given: No authentication token
    When: DELETE /api/workspaces/{id}
    Then: Returns 401 Unauthorized
    """
    response = await client.delete(f"/api/workspaces/{test_workspace_with_members.id}")

    assert response.status_code == 401
