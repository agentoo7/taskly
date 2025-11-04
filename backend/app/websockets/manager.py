"""
WebSocket connection manager for real-time updates.
Supports workspace rooms for broadcasting updates to all workspace members.
"""

import json

import structlog
from fastapi import WebSocket

logger = structlog.get_logger(__name__)


class ConnectionManager:
    def __init__(self):
        # Store active connections by workspace_id
        # workspace_id -> set of WebSocket connections
        self.workspace_connections: dict[str, set[WebSocket]] = {}

        # Store active connections by board_id
        # board_id -> set of WebSocket connections
        self.board_connections: dict[str, set[WebSocket]] = {}

        # Store user_id -> workspace_id mapping for cleanup
        self.user_workspaces: dict[str, set[str]] = {}

        # Store websocket -> user_id mapping
        self.connection_users: dict[WebSocket, str] = {}

    async def connect(self, websocket: WebSocket, workspace_id: str, user_id: str):
        """Add a new connection to a workspace room."""
        await websocket.accept()

        # Add to workspace room
        if workspace_id not in self.workspace_connections:
            self.workspace_connections[workspace_id] = set()
        self.workspace_connections[workspace_id].add(websocket)

        # Track user's workspaces
        if user_id not in self.user_workspaces:
            self.user_workspaces[user_id] = set()
        self.user_workspaces[user_id].add(workspace_id)

        # Track connection's user
        self.connection_users[websocket] = user_id

        logger.info(
            "websocket.connection.established",
            workspace_id=workspace_id,
            user_id=user_id,
            active_connections=len(self.workspace_connections.get(workspace_id, set())),
        )

    def disconnect(self, websocket: WebSocket, workspace_id: str):
        """Remove a connection from a workspace room."""
        if workspace_id in self.workspace_connections:
            self.workspace_connections[workspace_id].discard(websocket)

            # Clean up empty workspace rooms
            if not self.workspace_connections[workspace_id]:
                del self.workspace_connections[workspace_id]

        # Clean up user tracking
        user_id = self.connection_users.get(websocket)
        if user_id and user_id in self.user_workspaces:
            self.user_workspaces[user_id].discard(workspace_id)
            if not self.user_workspaces[user_id]:
                del self.user_workspaces[user_id]

        if websocket in self.connection_users:
            del self.connection_users[websocket]

        logger.info(
            "websocket.connection.closed",
            workspace_id=workspace_id,
            user_id=user_id,
            remaining_connections=len(self.workspace_connections.get(workspace_id, set())),
        )

    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send a message to a specific connection."""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error("websocket.send.failed", error=str(e))

    async def broadcast_to_workspace(
        self, workspace_id: str, message: dict, exclude_user_id: str | None = None
    ):
        """
        Broadcast a message to all connections in a workspace room.
        Optionally exclude the user who triggered the update.
        """
        if workspace_id not in self.workspace_connections:
            return

        connections = self.workspace_connections[workspace_id].copy()
        disconnected = set()

        for connection in connections:
            # Skip if this is the user who triggered the update
            if exclude_user_id and self.connection_users.get(connection) == exclude_user_id:
                continue

            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                logger.error("websocket.broadcast.failed", workspace_id=workspace_id, error=str(e))
                disconnected.add(connection)

        # Clean up disconnected connections
        for connection in disconnected:
            self.disconnect(connection, workspace_id)

        logger.info(
            "websocket.broadcast.complete",
            workspace_id=workspace_id,
            recipients=len(connections) - len(disconnected),
            excluded_user=exclude_user_id,
        )

    async def broadcast_to_board(
        self, board_id: str, message: dict, exclude_user_id: str | None = None
    ):
        """
        Broadcast a message to all connections viewing a specific board.
        Optionally exclude the user who triggered the update.
        """
        if board_id not in self.board_connections:
            return

        connections = self.board_connections[board_id].copy()
        disconnected = set()

        for connection in connections:
            # Skip if this is the user who triggered the update
            if exclude_user_id and self.connection_users.get(connection) == exclude_user_id:
                continue

            try:
                await connection.send_text(json.dumps(message))
            except Exception as e:
                logger.error("websocket.broadcast.failed", board_id=board_id, error=str(e))
                disconnected.add(connection)

        # Clean up disconnected connections
        for connection in disconnected:
            # Note: We don't have board_id in disconnect signature yet
            # For now, just remove from board_connections
            self.board_connections[board_id].discard(connection)

        if not self.board_connections[board_id]:
            del self.board_connections[board_id]

        logger.info(
            "websocket.broadcast.complete",
            board_id=board_id,
            recipients=len(connections) - len(disconnected),
            excluded_user=exclude_user_id,
        )


# Global connection manager instance
manager = ConnectionManager()
