"""
Vertical 9:16 Short-Form Reel Cropping Engine Module
"""

from typing import Optional, Tuple
import cv2
import numpy as np
from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.evaluation.vertical_crop")


class VerticalCropResult(BaseModel):
    """Schema representing vertical 9:16 crop dimensions and framing status."""
    aspect_ratio: str = "9:16"
    output_width: int = 1080
    output_height: int = 1920
    is_centered_on_ball: bool = True


class VerticalReelCropperEngine:
    """Crops 16:9 widescreen match footage into vertical 9:16 aspect ratio centered around ball tracking."""

    @staticmethod
    def crop_frame_to_vertical(
        frame: np.ndarray,
        ball_x_px: Optional[float] = None,
        ball_y_px: Optional[float] = None
    ) -> Tuple[np.ndarray, VerticalCropResult]:
        """Crops widescreen BGR frame into 9:16 aspect ratio centered around tracked ball coordinates."""
        if frame is None or frame.size == 0:
            return frame, VerticalCropResult(is_centered_on_ball=False)

        h, w = frame.shape[:2]
        crop_w = int(h * (9.0 / 16.0))

        if ball_x_px is not None:
            center_x = int(ball_x_px)
        else:
            center_x = w // 2

        x_start = max(0, min(w - crop_w, center_x - (crop_w // 2)))
        x_end = x_start + crop_w

        cropped = frame[:, x_start:x_end]
        resized = cv2.resize(cropped, (1080, 1920))

        logger.debug(f"Cropped Frame ({w}x{h}) -> Vertical 9:16 (1080x1920) centered at X={center_x}")

        return resized, VerticalCropResult(
            aspect_ratio="9:16",
            output_width=1080,
            output_height=1920,
            is_centered_on_ball=(ball_x_px is not None)
        )
