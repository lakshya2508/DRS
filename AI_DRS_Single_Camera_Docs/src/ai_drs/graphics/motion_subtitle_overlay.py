"""
Dynamic Motion Tracking Subtitle & Badge Overlay Engine
"""

import cv2
import numpy as np
from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.graphics.motion_subtitle")


class MotionSubtitleOverlayConfig(BaseModel):
    """Schema representing motion subtitle and speed badge overlay parameters."""
    speed_text: str = "145.2 KM/H"
    badge_type: str = "PERFECT_YORKER"
    subtitle_text: str = "WICKET! Clean bowled!"


class MotionSubtitleOverlayEngine:
    """Overlays animated speed badges, pitch zone tags, and dynamic subtitles onto vertical short video frames."""

    @staticmethod
    def draw_motion_overlays(frame: np.ndarray, config: MotionSubtitleOverlayConfig) -> np.ndarray:
        """Draws animated speed pill badge and dynamic subtitle text onto video frame."""
        if frame is None or frame.size == 0:
            return frame

        annotated = frame.copy()
        h, w = annotated.shape[:2]

        # Draw Speed Pill Badge near top center
        pill_w, pill_h = 240, 50
        px_start = (w - pill_w) // 2
        py_start = 120

        overlay = annotated.copy()
        cv2.rectangle(overlay, (px_start, py_start), (px_start + pill_w, py_start + pill_h), (0, 230, 118), -1)
        cv2.addWeighted(overlay, 0.9, annotated, 0.1, 0, annotated)

        cv2.putText(annotated, f"⚡ {config.speed_text}", (px_start + 15, py_start + 35), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)

        # Draw Dynamic Subtitle at bottom center
        sub_y = h - 180
        cv2.putText(annotated, config.subtitle_text, (50, sub_y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (0, 234, 255), 3)

        logger.debug(f"Applied Motion Subtitle Overlays: '{config.speed_text}', '{config.subtitle_text}'")
        return annotated
