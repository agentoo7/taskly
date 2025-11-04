"""
WebSocket endpoints for real-time updates.
"""

import structlog
from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_jwt_token
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.services.workspace_service import WorkspaceService
from app.websockets.manager import manager

logger = structlog.get_logger(__name__)

router = APIRouter()


async def get_current_user_ws(
    token: str = Query(..., alias="token"), db: AsyncSession = Depends(get_db)
) -> User:
    """
    Authenticate WebSocket connection via query parameter token.
    WebSocket connections can't use headers, so we use query params.
    """
    try:
        payload = decode_jwt_token(token)
        user_id = payload.get("sub")

        if not user_id:
            raise ValueError("Invalid token")

        user_repo = UserRepository(db)
        user = await user_repo.get(user_id)

        if not user:
            raise ValueError("User not found")

        return user
    except Exception as e:
        logger.error("websocket.auth.failed", error=str(e))
        raise


@router.websocket("/ws/workspaces/{workspace_id}")
async def workspace_websocket(
    websocket: WebSocket, workspace_id: str, db: AsyncSession = Depends(get_db)
):
    """
    WebSocket endpoint for workspace real-time updates.

    Clients connect with: ws://localhost:8000/ws/workspaces/{workspace_id}?token={access_token}

    Events sent to clients:
    - workspace_updated: { event: "workspace_updated", data: { workspace_id, name, updated_by } }
    - workspace_deleted: { event: "workspace_deleted", data: { workspace_id } }
    - member_added: { event: "member_added", data: { workspace_id, user_id, role } }
    - member_removed: { event: "member_removed", data: { workspace_id, user_id } }
    """
    # Accept connection first
    await websocket.accept()

    try:
        # Get token from query params
        token = websocket.query_params.get("token")
        if not token:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Missing token")
            return

        # Authenticate user
        try:
            payload = decode_jwt_token(token)
            user_id = payload.get("sub")
            if not user_id:
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Invalid token")
                return

            user_repo = UserRepository(db)
            user = await user_repo.get(user_id)
            if not user:
                await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="User not found")
                return
        except Exception as e:
            logger.error("websocket.auth.failed", error=str(e))
            await websocket.close(
                code=status.WS_1008_POLICY_VIOLATION, reason="Authentication failed"
            )
            return

        # Verify user has access to this workspace
        workspace_service = WorkspaceService(db)
        is_member = await workspace_service.check_workspace_member(workspace_id, user.id)
        if not is_member:
            await websocket.close(
                code=status.WS_1008_POLICY_VIOLATION, reason="Not a workspace member"
            )
            return

        # Connect to workspace room
        await manager.connect(websocket, workspace_id, str(user.id))

        # Send welcome message
        await manager.send_personal_message(
            {
                "event": "connected",
                "data": {"workspace_id": workspace_id, "message": "Connected to workspace updates"},
            },
            websocket,
        )

        # Keep connection alive and listen for client messages (optional)
        while True:
            try:
                # Wait for any client messages (we don't process them currently)
                data = await websocket.receive_text()
                logger.info(
                    "websocket.message.received",
                    workspace_id=workspace_id,
                    user_id=str(user.id),
                    message=data,
                )
            except WebSocketDisconnect:
                break

    except WebSocketDisconnect:
        logger.info("websocket.disconnect", workspace_id=workspace_id, user_id=str(user.id))
    except Exception as e:
        logger.error(
            "websocket.error", workspace_id=workspace_id, user_id=str(user.id), error=str(e)
        )
    finally:
        manager.disconnect(websocket, workspace_id)
