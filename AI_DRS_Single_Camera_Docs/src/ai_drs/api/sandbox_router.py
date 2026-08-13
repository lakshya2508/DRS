"""
Interactive Match Replay & 3D Sandbox REST Router
"""

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import HTMLResponse

from ai_drs.api.replay_controller import MatchReplayController, ReplayFrameState
from ai_drs.api.sandbox_component import WebGL3DSandboxComponent
from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.api.sandbox_router")

sandbox_router = APIRouter(prefix="/api/v1/sandbox", tags=["3D Replay Sandbox Engine"])


@sandbox_router.get("/viewer", response_class=HTMLResponse)
def get_3d_sandbox_viewer():
    """Returns HTML5 WebGL Interactive 3D Camera Free-Orbit Sandbox Viewer."""
    return HTMLResponse(content=WebGL3DSandboxComponent.render_3d_sandbox_html())


@sandbox_router.post("/seek/{match_id}", response_model=ReplayFrameState)
def seek_replay_frame(match_id: str, frame_index: int):
    """Seeks DVR match replay timeline to specific frame."""
    ctrl = MatchReplayController(match_id=match_id)
    return ctrl.seek_to_frame(frame_index)
