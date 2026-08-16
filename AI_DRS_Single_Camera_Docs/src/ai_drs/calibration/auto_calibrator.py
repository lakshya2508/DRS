"""
Auto Camera Calibration — Maps pixel coordinates to real-world pitch geometry
using reference points (crease lines, stumps) from a single calibration frame.
"""

import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Optional, Tuple

import cv2
import numpy as np

from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.calibration.auto_calibrator")


@dataclass
class CalibrationPoints:
    """Four reference points used for homography calibration."""
    # Pixel coordinates (x, y) in the camera frame
    batter_crease_left:  Tuple[float, float] = (0.0, 0.0)
    batter_crease_right: Tuple[float, float] = (0.0, 0.0)
    off_stump_base:      Tuple[float, float] = (0.0, 0.0)
    leg_stump_base:      Tuple[float, float] = (0.0, 0.0)

    # Real-world pitch dimensions (metres)
    # Standard ICC pitch: 20.12m from crease to crease, stumps 22.86cm wide
    real_pitch_length_m:  float = 20.12
    real_stump_width_m:   float = 0.2286


@dataclass
class CalibrationResult:
    is_calibrated:       bool = False
    homography_matrix:   Optional[List[List[float]]] = None
    pixels_per_metre_x:  float = 0.0
    pixels_per_metre_y:  float = 0.0
    stump_left_x:        float = 608.0
    stump_right_x:       float = 672.0
    crease_y:            float = 520.0
    popping_y:           float = 280.0
    wicket_top_y:        float = 445.0
    wicket_bottom_y:     float = 520.0
    frame_width:         int   = 1280
    frame_height:        int   = 720
    calibration_error_px: float = 0.0


class AutoCalibrator:
    """
    Automatic camera calibration using pitch geometry reference points.
    Supports both manual point selection and auto-detection via Hough lines.
    """

    def __init__(self):
        self._result = CalibrationResult()

    # ------------------------------------------------------------------
    # Manual calibration from known pixel points
    # ------------------------------------------------------------------

    def calibrate_from_points(self, points: CalibrationPoints,
                               frame_w: int = 1280, frame_h: int = 720) -> CalibrationResult:
        """Calibrate using four manually specified reference pixel coordinates."""
        bl = np.array(points.batter_crease_left)
        br = np.array(points.batter_crease_right)
        os = np.array(points.off_stump_base)
        ls = np.array(points.leg_stump_base)

        # Stump geometry
        stump_left_x  = min(ls[0], os[0])
        stump_right_x = max(ls[0], os[0])
        crease_y      = (bl[1] + br[1]) / 2.0
        wicket_bot_y  = (os[1] + ls[1]) / 2.0
        wicket_top_y  = wicket_bot_y - (stump_right_x - stump_left_x) * 2.5

        # Scale factors
        pixel_stump_width = stump_right_x - stump_left_x
        px_per_m_x = pixel_stump_width / points.real_stump_width_m if pixel_stump_width > 0 else 50.0
        pitch_px   = abs(crease_y - wicket_bot_y)
        px_per_m_y = pitch_px / points.real_pitch_length_m if pitch_px > 0 else 25.0

        self._result = CalibrationResult(
            is_calibrated      = True,
            pixels_per_metre_x = round(px_per_m_x, 2),
            pixels_per_metre_y = round(px_per_m_y, 2),
            stump_left_x       = round(stump_left_x, 1),
            stump_right_x      = round(stump_right_x, 1),
            crease_y           = round(crease_y, 1),
            popping_y          = round(wicket_top_y - pitch_px * 0.05, 1),
            wicket_top_y       = round(wicket_top_y, 1),
            wicket_bottom_y    = round(wicket_bot_y, 1),
            frame_width        = frame_w,
            frame_height       = frame_h,
            calibration_error_px = 0.0,
        )
        logger.info(f"Calibration complete — px/m: x={px_per_m_x:.1f}, y={px_per_m_y:.1f} | "
                    f"stumps: [{stump_left_x:.0f}, {stump_right_x:.0f}]")
        return self._result

    # ------------------------------------------------------------------
    # Auto-calibration from a frame image (Hough line detection)
    # ------------------------------------------------------------------

    def auto_calibrate_from_frame(self, frame: np.ndarray) -> CalibrationResult:
        """Attempt automatic calibration by detecting crease lines in the frame."""
        h, w = frame.shape[:2]
        gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, threshold=80,
                                 minLineLength=w//6, maxLineGap=30)

        horizontal_lines = []
        if lines is not None:
            for line in lines:
                pts = line.flatten()
                x1, y1, x2, y2 = int(pts[0]), int(pts[1]), int(pts[2]), int(pts[3])
                angle = abs(np.degrees(np.arctan2(y2 - y1, x2 - x1)))
                if angle < 12:  # nearly horizontal
                    y_mid = (y1 + y2) / 2
                    horizontal_lines.append(y_mid)

        horizontal_lines.sort()

        if len(horizontal_lines) >= 2:
            crease_y  = horizontal_lines[-1]   # lowest = batter crease
            popping_y = horizontal_lines[0]    # highest = bowler crease
            stump_cx  = w / 2
            stump_half = w * 0.035
            result = CalibrationResult(
                is_calibrated    = True,
                stump_left_x     = round(stump_cx - stump_half, 1),
                stump_right_x    = round(stump_cx + stump_half, 1),
                crease_y         = round(crease_y, 1),
                popping_y        = round(popping_y, 1),
                wicket_top_y     = round(crease_y - (crease_y - popping_y) * 0.15, 1),
                wicket_bottom_y  = round(crease_y, 1),
                frame_width      = w,
                frame_height     = h,
                calibration_error_px = 3.5,
            )
            logger.info("Auto-calibration succeeded from Hough line detection.")
        else:
            logger.warning("Auto-calibration failed — using default geometry.")
            result = CalibrationResult(is_calibrated=False,
                                       frame_width=w, frame_height=h)

        self._result = result
        return result

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def save(self, path: str):
        Path(path).write_text(json.dumps(asdict(self._result), indent=2))
        logger.info(f"Calibration saved: {path}")

    def load(self, path: str) -> CalibrationResult:
        data = json.loads(Path(path).read_text())
        self._result = CalibrationResult(**data)
        logger.info(f"Calibration loaded: {path}")
        return self._result

    @property
    def result(self) -> CalibrationResult:
        return self._result

    def get_pitch_geometry(self) -> dict:
        """Returns PITCH_GEOMETRY dict compatible with lbw_pipeline zone classifiers."""
        r = self._result
        return {
            "stump_left_x":    r.stump_left_x,
            "stump_right_x":   r.stump_right_x,
            "crease_y":        r.crease_y,
            "popping_y":       r.popping_y,
            "wicket_top_y":    r.wicket_top_y,
            "wicket_bottom_y": r.wicket_bottom_y,
        }
