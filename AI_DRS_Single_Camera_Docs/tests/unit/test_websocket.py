"""
Unit tests for Real-Time WebSocket Broadcast Manager and Endpoint
"""

import time
from fastapi.testclient import TestClient
import pytest

from ai_drs.api.main import app
from ai_drs.api.websocket_manager import BroadcastEvent, ws_manager

client = TestClient(app)


def test_websocket_broadcast_and_channel_isolation():
    match_a = "MATCH_WS_101"
    match_b = "MATCH_WS_102"

    with client.websocket_connect(f"/ws/match/{match_a}") as ws_a1:
        with client.websocket_connect(f"/ws/match/{match_a}") as ws_a2:
            with client.websocket_connect(f"/ws/match/{match_b}") as ws_b1:

                # Verify connection counts
                assert len(ws_manager.active_connections[match_a]) == 2
                assert len(ws_manager.active_connections[match_b]) == 1

                # Broadcast event to Match A
                event_a = BroadcastEvent(
                    event_type="DELIVERY_UPDATE",
                    match_id=match_a,
                    timestamp=time.time(),
                    data={"score": "15/0", "runs": 4}
                )

                # Use asyncio run or sync broadcast call
                import asyncio
                asyncio.run(ws_manager.broadcast_match_event(event_a))

                # Clients on Match A should receive payload
                data_a1 = ws_a1.receive_json()
                assert data_a1["event_type"] == "DELIVERY_UPDATE"
                assert data_a1["data"]["score"] == "15/0"

                data_a2 = ws_a2.receive_json()
                assert data_a2["event_type"] == "DELIVERY_UPDATE"

                # Client on Match B should NOT have received event_a
                # Broadcast event to Match B
                event_b = BroadcastEvent(
                    event_type="DRS_DECISION",
                    match_id=match_b,
                    timestamp=time.time(),
                    data={"result": "OUT"}
                )
                asyncio.run(ws_manager.broadcast_match_event(event_b))

                data_b1 = ws_b1.receive_json()
                assert data_b1["event_type"] == "DRS_DECISION"
                assert data_b1["data"]["result"] == "OUT"

    # Disconnected clients cleaned up
    assert match_a not in ws_manager.active_connections
    assert match_b not in ws_manager.active_connections
