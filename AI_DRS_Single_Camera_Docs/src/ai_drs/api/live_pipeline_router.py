"""
Live Pipeline WebSocket Router — streams real-time LBW decisions and MJPEG
annotated frames to all connected clients (dashboard, scoreboard, mobile app).
"""

import asyncio
import base64
import json
import time
import threading
from typing import Dict, Set, Optional

import cv2
import numpy as np
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from ai_drs.common.logging import setup_logger
from ai_drs.pipeline.camera_processor import CameraSource, LiveCameraProcessor
from ai_drs.pipeline.lbw_pipeline import LiveLBWDecision, LiveLBWPipeline

logger = setup_logger("ai_drs.api.live_pipeline")

live_pipeline_router = APIRouter(tags=["Live Camera Pipeline"])
router = live_pipeline_router

# ─── Global pipeline state ──────────────────────────────────────────────────
_processor: Optional[LiveCameraProcessor] = None
_pipeline:  Optional[LiveLBWPipeline]     = None
_latest_decision: Optional[dict]          = None
_latest_jpeg:     Optional[bytes]         = None
_ws_clients:      Set[WebSocket]          = set()
_state_lock       = threading.Lock()


def _on_frame(cam_frame):
    """Called on every captured frame — runs pipeline and broadcasts to WS clients."""
    global _latest_decision, _latest_jpeg
    if _pipeline is None:
        return

    decision = _pipeline.process_frame(cam_frame)

    # JPEG encode annotated frame
    if decision.annotated_frame is not None:
        ret, buf = cv2.imencode(".jpg", decision.annotated_frame,
                                [cv2.IMWRITE_JPEG_QUALITY, 75])
        jpeg = buf.tobytes() if ret else b""
    else:
        jpeg = b""

    payload = {
        "decision_id":    decision.decision_id,
        "frame_id":       decision.frame_id,
        "verdict":        decision.verdict,
        "pitching_zone":  decision.pitching_zone,
        "impact_zone":    decision.impact_zone,
        "wicket_zone":    decision.wicket_zone,
        "confidence_pct": decision.confidence_pct,
        "ball_speed_kmh": decision.ball_speed_kmh,
        "voice_callout":  decision.voice_callout,
        "trajectory":     decision.trajectory[-10:],
        "frame_b64":      base64.b64encode(jpeg).decode() if jpeg else "",
        "timestamp":      decision.timestamp,
    }

    with _state_lock:
        _latest_decision = payload
        _latest_jpeg     = jpeg

    # Async broadcast — schedule on event loop
    asyncio.run(_broadcast(json.dumps(payload)))


async def _broadcast(message: str):
    dead = set()
    for ws in list(_ws_clients):
        try:
            await ws.send_text(message)
        except Exception:
            dead.add(ws)
    _ws_clients.difference_update(dead)


# ─── REST control endpoints ──────────────────────────────────────────────────

@live_pipeline_router.post("/pipeline/start")
def start_pipeline(source: str = "SYNTHETIC", source_path: str = "0"):
    """
    Start the live camera pipeline.
    source: SYNTHETIC | WEBCAM | VIDEO | RTSP
    source_path: '0' for webcam, RTSP URL, or path to video file.
    """
    global _processor, _pipeline
    if _processor and _processor.is_running:
        return {"status": "already_running"}

    src = CameraSource(source.upper()) if source.upper() in CameraSource.__members__ else CameraSource.SYNTHETIC
    _pipeline  = LiveLBWPipeline()
    _processor = LiveCameraProcessor(
        source      = src,
        source_path = source_path,
        target_fps  = 30,
        on_frame    = _on_frame,
    )
    _processor.start()
    return {"status": "started", "source": src.value, "source_path": source_path}


@live_pipeline_router.post("/pipeline/stop")
def stop_pipeline():
    """Stop the live camera pipeline."""
    global _processor, _pipeline
    if _processor:
        _processor.stop()
        _processor = None
    _pipeline = None
    return {"status": "stopped"}


@live_pipeline_router.post("/pipeline/reset_delivery")
def reset_delivery():
    """Reset trajectory buffer between deliveries."""
    if _pipeline:
        _pipeline.reset_delivery()
        return {"status": "delivery_reset"}
    return {"status": "pipeline_not_running"}


@live_pipeline_router.get("/pipeline/status")
def pipeline_status():
    """Get current pipeline status and latest decision."""
    running = bool(_processor and _processor.is_running)
    with _state_lock:
        decision = _latest_decision
    return {
        "running":         running,
        "latest_decision": decision,
    }


@live_pipeline_router.get("/pipeline/frame")
def get_latest_frame_jpeg():
    """Returns the latest annotated frame as base64 JPEG string."""
    with _state_lock:
        jpeg = _latest_jpeg
    if not jpeg:
        return {"frame_b64": ""}
    return {"frame_b64": base64.b64encode(jpeg).decode()}


# ─── WebSocket endpoint ──────────────────────────────────────────────────────

@live_pipeline_router.websocket("/ws/live")
async def websocket_live(websocket: WebSocket):
    """
    WebSocket endpoint — connects dashboard, scoreboard, mobile app.
    Receives real-time LBW decisions + annotated frame (base64 JPEG) on every frame.
    """
    await websocket.accept()
    _ws_clients.add(websocket)
    logger.info(f"WebSocket client connected — total={len(_ws_clients)}")
    try:
        # Send current pipeline status immediately on connect
        await websocket.send_text(json.dumps({
            "type": "connected",
            "pipeline_running": bool(_processor and _processor.is_running),
        }))
        while True:
            # Keep connection alive — client may send "reset" commands
            data = await websocket.receive_text()
            if data.strip().lower() == "reset":
                reset_delivery()
                await websocket.send_text(json.dumps({"type": "delivery_reset"}))
    except WebSocketDisconnect:
        _ws_clients.discard(websocket)
        logger.info(f"WebSocket client disconnected — total={len(_ws_clients)}")
