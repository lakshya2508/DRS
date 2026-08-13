"""
Dense Optical Flow Ball Seam Spin Rate Estimator Module
"""

import math
from typing import Optional, Tuple
import cv2
import numpy as np
from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.vision.optical_flow")


class BallSpinEstimate(BaseModel):
    """Schema representing estimated ball seam spin RPM and rotation axis."""
    spin_rpm: float = Field(ge=0.0)
    rotation_axis_angle_deg: float = Field(ge=0.0, le=360.0)
    mean_flow_magnitude: float = Field(ge=0.0)
    confidence: float = Field(ge=0.0, le=1.0)


class OpticalFlowSpinEstimator:
    """Estimates ball seam rotation speed (RPM) using OpenCV Farneback Dense Optical Flow."""

    @staticmethod
    def estimate_ball_spin(
        prev_crop: np.ndarray,
        curr_crop: np.ndarray,
        fps: float = 240.0,
        ball_radius_px: float = 20.0
    ) -> BallSpinEstimate:
        """Calculates optical flow vectors between consecutive high-speed crops to estimate spin RPM."""
        if prev_crop.shape != curr_crop.shape or prev_crop.size == 0:
            return BallSpinEstimate(spin_rpm=0.0, rotation_axis_angle_deg=0.0, mean_flow_magnitude=0.0, confidence=0.0)

        # Convert to grayscale
        prev_gray = cv2.cvtColor(prev_crop, cv2.COLOR_BGR2GRAY) if len(prev_crop.shape) == 3 else prev_crop
        curr_gray = cv2.cvtColor(curr_crop, cv2.COLOR_BGR2GRAY) if len(curr_crop.shape) == 3 else curr_crop

        # Compute Farneback Optical Flow
        flow = cv2.calcOpticalFlowFarneback(
            prev_gray, curr_gray, None,
            pyr_scale=0.5, levels=3, winsize=15, iterations=3, poly_n=5, poly_sigma=1.2, flags=0
        )

        fx, fy = flow[..., 0], flow[..., 1]
        magnitude, angle = cv2.cartToPolar(fx, fy, angleInDegrees=True)

        mean_mag = float(np.mean(magnitude))
        mean_ang = float(np.mean(angle)) if mean_mag > 0 else 0.0

        # Angular velocity omega = (v_px / radius_px) * fps (rad/s) -> RPM = (omega * 60) / (2 * pi)
        omega = (mean_mag / max(1.0, ball_radius_px)) * fps
        rpm = float((omega * 60.0) / (2.0 * math.pi))
        conf = min(0.95, max(0.40, mean_mag / 5.0))

        logger.info(f"Optical Flow Ball Spin: RPM={rpm:.1f}, axis_angle={mean_ang:.1f}deg, conf={conf:.2f}")

        return BallSpinEstimate(
            spin_rpm=round(rpm, 1),
            rotation_axis_angle_deg=round(mean_ang, 1),
            mean_flow_magnitude=round(mean_mag, 3),
            confidence=round(conf, 2)
        )
