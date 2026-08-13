"""
VR Pitch Teleportation REST Router
"""

from typing import List
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.api.vr")

vr_router = APIRouter(prefix="/api/v1/vr", tags=["VR Spatial Engine"])


class VRPitchViewpoint(BaseModel):
    viewpoint_id: str
    viewpoint_name: str
    camera_pos_xyz: List[float]
    skybox_texture_url: str


@vr_router.get("/viewpoints", response_model=List[VRPitchViewpoint])
def list_vr_viewpoints():
    """Returns available VR headset pitch teleportation camera viewpoints."""
    viewpoints = [
        VRPitchViewpoint(
            viewpoint_id="VR_FIRST_SLIP",
            viewpoint_name="First Slip Eye-Level VR Perspective",
            camera_pos_xyz=[-0.8, 18.0, 1.6],
            skybox_texture_url="https://cdn.aidrs.io/vr/first_slip_skybox.png"
        ),
        VRPitchViewpoint(
            viewpoint_id="VR_BOWLER_END",
            viewpoint_name="Bowler Release High Angle VR Perspective",
            camera_pos_xyz=[0.0, -2.0, 3.5],
            skybox_texture_url="https://cdn.aidrs.io/vr/bowler_end_skybox.png"
        ),
    ]
    logger.info("Served VR Headset Pitch Teleportation Viewpoints list.")
    return viewpoints
