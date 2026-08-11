"""
Stump and Wicket Geometry Detection Module for AI DRS
"""

from typing import List, Optional, Tuple
import cv2
import numpy as np
from pydantic import BaseModel, Field

from ai_drs.calibration.pitch_calibration import CalibrationData, PitchCalibrator, Point2D
from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.detection.stump")

# Standard Wicket Physical Dimensions (meters)
STUMP_WIDTH_TOTAL_M = 0.2286   # 9 inches (outer off to outer leg)
STUMP_HEIGHT_M = 0.7112        # 28 inches height above ground
OFF_STUMP_OFFSET_M = -0.1143   # -4.5 inches
LEG_STUMP_OFFSET_M = 0.1143    # +4.5 inches


class StumpDetection(BaseModel):
    """Represents an individual detected stump in image space."""
    stump_name: str = Field(description="Name of stump: 'off', 'middle', 'leg'")
    bbox: Tuple[float, float, float, float] = Field(description="(x_min, y_min, x_max, y_max)")
    base_pixel: Point2D = Field(description="Ground base point in image space")
    top_pixel: Point2D = Field(description="Stump top point in image space")
    confidence: float = Field(ge=0.0, le=1.0)


class WicketGeometry(BaseModel):
    """Represents overall detected wicket and pitch ground geometry."""
    wicket_y_m: float = Field(default=20.12, description="Distance to batter wicket plane in meters")
    stump_width_m: float = Field(default=STUMP_WIDTH_TOTAL_M)
    stump_height_m: float = Field(default=STUMP_HEIGHT_M)
    off_stump_x_m: float = Field(default=OFF_STUMP_OFFSET_M)
    leg_stump_x_m: float = Field(default=LEG_STUMP_OFFSET_M)
    stumps: List[StumpDetection] = Field(default_factory=list)
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    is_valid: bool = Field(default=True)


class StumpDetector:
    """Detects stumps and computes metric wicket plane geometry in camera image space."""

    def __init__(self, min_confidence: float = 0.4):
        self.min_confidence = min_confidence

    def detect_stumps(
        self,
        image: np.ndarray,
        calibration: Optional[CalibrationData] = None
    ) -> WicketGeometry:
        """Detects stumps in image using classical edge filtering and calibration projection."""
        if image is None or image.size == 0:
            return WicketGeometry(is_valid=False, confidence=0.0)

        stumps_detected: List[StumpDetection] = []

        # If calibration is available, project theoretical 3D stump base and top positions into image
        if calibration is not None and calibration.is_valid:
            H_inv = calibration.inv_homography_matrix
            # Pitch ground bases (in meters)
            off_base_pitch = Point2D(x=OFF_STUMP_OFFSET_M, y=calibration.pitch_points[1].y if len(calibration.pitch_points) > 1 else 20.12)
            mid_base_pitch = Point2D(x=0.0, y=calibration.pitch_points[1].y if len(calibration.pitch_points) > 1 else 20.12)
            leg_base_pitch = Point2D(x=LEG_STUMP_OFFSET_M, y=calibration.pitch_points[1].y if len(calibration.pitch_points) > 1 else 20.12)

            # Project base ground pixels
            off_base_img = PitchCalibrator.pitch_to_image(off_base_pitch, H_inv)
            mid_base_img = PitchCalibrator.pitch_to_image(mid_base_pitch, H_inv)
            leg_base_img = PitchCalibrator.pitch_to_image(leg_base_pitch, H_inv)

            # Estimate stump top pixels (assuming vertical upward direction in image, approx 40-80px high depending on view)
            stump_height_px = max(20.0, (image.shape[0] * 0.15))

            stumps_detected = [
                StumpDetection(
                    stump_name="off",
                    bbox=(off_base_img.x - 5, off_base_img.y - stump_height_px, off_base_img.x + 5, off_base_img.y),
                    base_pixel=off_base_img,
                    top_pixel=Point2D(x=off_base_img.x, y=off_base_img.y - stump_height_px),
                    confidence=0.90
                ),
                StumpDetection(
                    stump_name="middle",
                    bbox=(mid_base_img.x - 5, mid_base_img.y - stump_height_px, mid_base_img.x + 5, mid_base_img.y),
                    base_pixel=mid_base_img,
                    top_pixel=Point2D(x=mid_base_img.x, y=mid_base_img.y - stump_height_px),
                    confidence=0.95
                ),
                StumpDetection(
                    stump_name="leg",
                    bbox=(leg_base_img.x - 5, leg_base_img.y - stump_height_px, leg_base_img.x + 5, leg_base_img.y),
                    base_pixel=leg_base_img,
                    top_pixel=Point2D(x=leg_base_img.x, y=leg_base_img.y - stump_height_px),
                    confidence=0.90
                )
            ]

            logger.info("Localized stumps using camera calibration projection.")
            return WicketGeometry(
                stumps=stumps_detected,
                confidence=0.92,
                is_valid=True
            )

        # Fallback to classical vertical edge detection when no calibration is provided
        classical_stumps = self._classical_stump_search(image)
        if classical_stumps:
            return WicketGeometry(
                stumps=classical_stumps,
                confidence=0.70,
                is_valid=True
            )

        logger.warning("Stump detection yielded low confidence / no stumps.")
        return WicketGeometry(is_valid=False, confidence=0.0)

    def _classical_stump_search(self, image: np.ndarray) -> List[StumpDetection]:
        """Classical image processing using vertical Sobel filter and line grouping."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        # Vertical Sobel gradient filter
        sobel_x = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        abs_sobel_x = np.uint8(np.absolute(sobel_x))
        _, thresh = cv2.threshold(abs_sobel_x, 50, 255, cv2.THRESH_BINARY)

        lines = cv2.HoughLinesP(thresh, 1, np.pi / 180, threshold=40, minLineLength=30, maxLineGap=10)
        if lines is None:
            return []
        vertical_lines = []
        for line in lines:
            x1, y1, x2, y2 = line.reshape(4)
            angle = np.abs(np.arctan2(y2 - y1, x2 - x1) * 180.0 / np.pi)
            if 75.0 <= angle <= 105.0:  # Near vertical
                vertical_lines.append((x1, y1, x2, y2))

        if not vertical_lines:
            return []

        # Find median center of vertical lines
        xs = [(l[0] + l[2]) / 2.0 for l in vertical_lines]
        ys_min = [min(l[1], l[3]) for l in vertical_lines]
        ys_max = [max(l[1], l[3]) for l in vertical_lines]

        mid_x = float(np.median(xs))
        min_y = float(np.min(ys_min))
        max_y = float(np.max(ys_max))

        # Create 3 estimated stumps around mid_x
        stump_spacing = 15.0
        return [
            StumpDetection(
                stump_name="off",
                bbox=(mid_x - stump_spacing - 5, min_y, mid_x - stump_spacing + 5, max_y),
                base_pixel=Point2D(x=mid_x - stump_spacing, y=max_y),
                top_pixel=Point2D(x=mid_x - stump_spacing, y=min_y),
                confidence=0.70
            ),
            StumpDetection(
                stump_name="middle",
                bbox=(mid_x - 5, min_y, mid_x + 5, max_y),
                base_pixel=Point2D(x=mid_x, y=max_y),
                top_pixel=Point2D(x=mid_x, y=min_y),
                confidence=0.75
            ),
            StumpDetection(
                stump_name="leg",
                bbox=(mid_x + stump_spacing - 5, min_y, mid_x + stump_spacing + 5, max_y),
                base_pixel=Point2D(x=mid_x + stump_spacing, y=max_y),
                top_pixel=Point2D(x=mid_x + stump_spacing, y=min_y),
                confidence=0.70
            )
        ]
