"""
Event Detection Module for AI DRS (Pitching & Impact Localization and Zone Classification)
"""

from typing import List, Optional, Tuple
import numpy as np
from pydantic import BaseModel, Field

from ai_drs.calibration.pitch_calibration import CalibrationData, PitchCalibrator, Point2D
from ai_drs.common.logging import setup_logger
from ai_drs.detection.stump_detector import OFF_STUMP_OFFSET_M, LEG_STUMP_OFFSET_M
from ai_drs.tracking.ball_tracker import BallTrack, TrackedPoint

logger = setup_logger("ai_drs.events")


class PitchingEvent(BaseModel):
    """Schema representing detected ball pitching (bounce) event."""
    frame_id: int = Field(ge=0)
    pixel_point: Point2D = Field(description="Bounce point in image pixels")
    metric_point: Point2D = Field(description="Bounce point on pitch ground in meters (X,Y)")
    zone: str = Field(description="Pitching zone: 'IN_LINE', 'OUTSIDE_OFF', 'OUTSIDE_LEG'")
    confidence: float = Field(ge=0.0, le=1.0)


class ImpactEvent(BaseModel):
    """Schema representing detected ball-pad/batsman impact event."""
    frame_id: int = Field(ge=0)
    pixel_point: Point2D = Field(description="Impact point in image pixels")
    metric_point: Point2D = Field(description="Impact point on pitch ground in meters (X,Y)")
    zone: str = Field(description="Impact zone: 'IN_LINE', 'OUTSIDE_OFF', 'OUTSIDE_LEG'")
    confidence: float = Field(ge=0.0, le=1.0)


class EventDetector:
    """Detects pitching (bounce) and impact events and classifies pitch zones."""

    def __init__(self, default_stance: str = "RHB"):
        self.default_stance = default_stance.upper()

    @staticmethod
    def classify_zone(x_meters: float, batter_stance: str = "RHB") -> str:
        """Classifies a ground X coordinate into IN_LINE, OUTSIDE_OFF, or OUTSIDE_LEG.
        Off stump is at -0.1143m, Leg stump is at +0.1143m for RHB.
        """
        if OFF_STUMP_OFFSET_M <= x_meters <= LEG_STUMP_OFFSET_M:
            return "IN_LINE"

        if batter_stance.upper() == "RHB":
            return "OUTSIDE_OFF" if x_meters < OFF_STUMP_OFFSET_M else "OUTSIDE_LEG"
        else:  # LHB
            return "OUTSIDE_LEG" if x_meters < OFF_STUMP_OFFSET_M else "OUTSIDE_OFF"

    def detect_pitching(
        self,
        track: BallTrack,
        calibration: Optional[CalibrationData] = None,
        batter_stance: Optional[str] = None
    ) -> Optional[PitchingEvent]:
        """Localizes ball bounce / pitching frame and metric coordinates."""
        if track is None or len(track.points) < 3:
            logger.warning("Insufficient track points for pitching detection.")
            return None

        stance = batter_stance or self.default_stance

        # Extract image Y positions (bounce appears as local maximum in image pixel Y if 0 is top)
        pixel_ys = [p.y for p in track.points]

        # Find local maximum in image Y (lowest physical point of trajectory arc)
        bounce_idx = int(np.argmax(pixel_ys))

        # Boundary checks: bounce should not be at exact start/end of track
        if bounce_idx == 0 or bounce_idx == len(track.points) - 1:
            # Fallback to middle frame if trajectory arc peak is not prominent
            bounce_idx = len(track.points) // 2

        bounce_pt = track.points[bounce_idx]
        pixel_point = Point2D(x=bounce_pt.x, y=bounce_pt.y)

        if calibration is not None and calibration.is_valid:
            metric_pt = PitchCalibrator.image_to_pitch(pixel_point, calibration.homography_matrix)
        else:
            # Synthetic default metric mapping if uncalibrated
            metric_pt = Point2D(x=0.0, y=10.0)

        zone = self.classify_zone(metric_pt.x, batter_stance=stance)
        conf = min(1.0, max(0.4, bounce_pt.confidence * 0.9))

        logger.info(
            f"Detected Pitching: frame={bounce_pt.frame_id}, "
            f"metric=({metric_pt.x:.2f}m, {metric_pt.y:.2f}m), zone={zone}, conf={conf:.2f}"
        )

        return PitchingEvent(
            frame_id=bounce_pt.frame_id,
            pixel_point=pixel_point,
            metric_point=metric_pt,
            zone=zone,
            confidence=conf
        )

    def detect_impact(
        self,
        track: BallTrack,
        calibration: Optional[CalibrationData] = None,
        batter_stance: Optional[str] = None,
        pad_bbox: Optional[Tuple[float, float, float, float]] = None
    ) -> Optional[ImpactEvent]:
        """Localizes ball-pad impact frame and metric coordinates."""
        if track is None or len(track.points) < 3:
            logger.warning("Insufficient track points for impact detection.")
            return None

        stance = batter_stance or self.default_stance

        # Impact typically occurs near the end of the ball track near pad/batter
        impact_idx = len(track.points) - 1

        # If pad bbox provided, find point closest to pad bbox
        if pad_bbox is not None:
            px1, py1, px2, py2 = pad_bbox
            pad_cx = (px1 + px2) / 2.0
            pad_cy = (py1 + py2) / 2.0

            min_dist = float("inf")
            for idx, p in enumerate(track.points):
                dist = np.hypot(p.x - pad_cx, p.y - pad_cy)
                if dist < min_dist:
                    min_dist = dist
                    impact_idx = idx

        impact_pt = track.points[impact_idx]
        pixel_point = Point2D(x=impact_pt.x, y=impact_pt.y)

        if calibration is not None and calibration.is_valid:
            metric_pt = PitchCalibrator.image_to_pitch(pixel_point, calibration.homography_matrix)
        else:
            metric_pt = Point2D(x=0.0, y=18.5)

        zone = self.classify_zone(metric_pt.x, batter_stance=stance)
        conf = min(1.0, max(0.4, impact_pt.confidence * 0.85))

        logger.info(
            f"Detected Impact: frame={impact_pt.frame_id}, "
            f"metric=({metric_pt.x:.2f}m, {metric_pt.y:.2f}m), zone={zone}, conf={conf:.2f}"
        )

        return ImpactEvent(
            frame_id=impact_pt.frame_id,
            pixel_point=pixel_point,
            metric_point=metric_pt,
            zone=zone,
            confidence=conf
        )
