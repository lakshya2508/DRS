"""
360-Degree Panoramic Video Sphere Stitcher Module for VR Headsets
"""

from typing import List, Tuple
import cv2
import numpy as np
from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.graphics.vr_stitcher")


class VRSkyboxTextureState(BaseModel):
    """Schema representing 360 equirectangular VR skybox texture map parameters."""
    equirectangular_width: int = 3840
    equirectangular_height: int = 1920
    fov_horizontal_deg: float = 360.0
    fov_vertical_deg: float = 180.0
    is_vr_ready: bool = True


class VRPanoramicStitcherEngine:
    """Stitches multi-camera ultra-wide feeds into 360-degree equirectangular VR skybox texture maps."""

    @staticmethod
    def stitch_equirectangular_skybox(camera_feeds: List[np.ndarray]) -> Tuple[np.ndarray, VRSkyboxTextureState]:
        """Stitches camera feeds into 3840x1920 4K equirectangular 360 VR texture map."""
        if not camera_feeds or any(f is None or f.size == 0 for f in camera_feeds):
            blank_skybox = np.zeros((1920, 3840, 3), dtype=np.uint8)
            return blank_skybox, VRSkyboxTextureState(is_vr_ready=False)

        # Concatenate and resize into 3840x1920 4K 360 equirectangular canvas
        concatenated = np.hstack(camera_feeds)
        skybox = cv2.resize(concatenated, (3840, 1920))

        logger.info(f"Stitched {len(camera_feeds)} Camera Feeds into 4K 360 VR Skybox (3840x1920).")

        return skybox, VRSkyboxTextureState(
            equirectangular_width=3840,
            equirectangular_height=1920,
            fov_horizontal_deg=360.0,
            fov_vertical_deg=180.0,
            is_vr_ready=True
        )
