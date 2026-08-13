"""
Virtual Turf Sponsor Logo Overlay Generator Module
"""

import cv2
import numpy as np
from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.graphics.virtual_sponsor")


class VirtualSponsorOverlayConfig(BaseModel):
    """Schema representing virtual turf brand logo placement parameters."""
    sponsor_name: str = "EMIRATES"
    position_x_m: float = -5.0
    position_y_m: float = 10.0
    logo_width_m: float = 4.0
    opacity: float = Field(default=0.85, ge=0.0, le=1.0)


class VirtualTurfSponsorOverlayEngine:
    """Dynamically projects perspective-warped virtual brand logos onto outfield grass."""

    @staticmethod
    def draw_virtual_sponsor_logo(frame: np.ndarray, config: VirtualSponsorOverlayConfig) -> np.ndarray:
        """Projects virtual brand logo onto ground turf within video frame."""
        if frame is None or frame.size == 0:
            return frame

        annotated = frame.copy()
        h, w = annotated.shape[:2]

        # Draw perspective warped logo box near bottom left outfield
        pts = np.array([[100, h - 200], [350, h - 250], [420, h - 120], [120, h - 100]], dtype=np.int32)

        overlay = annotated.copy()
        cv2.fillPoly(overlay, [pts], (220, 50, 0))
        cv2.addWeighted(overlay, config.opacity, annotated, 1.0 - config.opacity, 0, annotated)

        cv2.putText(annotated, config.sponsor_name, (160, h - 150), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 255, 255), 2)

        logger.debug(f"Projected Virtual Turf Sponsor Logo [{config.sponsor_name}] onto ground.")
        return annotated
