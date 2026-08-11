"""
Multi-User Real-Time WebSocket Broadcast Manager for AI DRS & Match Engine
"""

import json
from typing import Dict, List, Set
from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.api.websocket")


class BroadcastEvent(BaseModel):
    """Schema representing a real-time WebSocket broadcast message."""
    event_type: str = Field(description="'DELIVERY_UPDATE', 'SCOREBOARD_UPDATE', 'DRS_DECISION', 'TOSS_UPDATE'")
    match_id: str
    timestamp: float
    data: Dict


class WebSocketBroadcastManager:
    """Manages active WebSocket connections per match channel and broadcasts real-time updates."""

    def __init__(self):
        # Match ID -> Set of active WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}

    async def connect(self, match_id: str, websocket: WebSocket):
        """Accepts WebSocket connection and registers client under match channel."""
        await websocket.accept()
        if match_id not in self.active_connections:
            self.active_connections[match_id] = set()
        self.active_connections[match_id].add(websocket)
        logger.info(f"WebSocket client connected to Match [{match_id}]. Total clients: {len(self.active_connections[match_id])}")

    def disconnect(self, match_id: str, websocket: WebSocket):
        """Removes disconnected client from match channel."""
        if match_id in self.active_connections:
            self.active_connections[match_id].discard(websocket)
            if not self.active_connections[match_id]:
                del self.active_connections[match_id]
        logger.info(f"WebSocket client disconnected from Match [{match_id}].")

    async def broadcast_match_event(self, event: BroadcastEvent):
        """Broadcasts a JSON event payload to all connected clients on a specific match channel."""
        match_id = event.match_id
        if match_id not in self.active_connections or not self.active_connections[match_id]:
            return

        message_json = event.model_dump_json()
        stale_sockets = []

        for socket in list(self.active_connections[match_id]):
            try:
                await socket.send_text(message_json)
            except Exception as e:
                logger.warning(f"Error sending to WebSocket client on Match [{match_id}]: {e}")
                stale_sockets.append(socket)

        for stale in stale_sockets:
            self.disconnect(match_id, stale)


# Global broadcast manager instance
ws_manager = WebSocketBroadcastManager()
