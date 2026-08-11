"""
Camera and Pitch Homography Calibration Module for AI DRS
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import cv2
import numpy as np
from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.calibration")

# Standard Cricket Pitch Dimensions (in meters)
STANDARD_PITCH_LENGTH_M = 20.12  # Stump to stump
STANDARD_PITCH_WIDTH_M = 3.05    # Pitch width (10 ft)
POPPING_CREASE_DIST_M = 1.22     # Distance from stump line to popping crease
CREASE_WIDTH_M = 2.64            # Return crease width


class Point2D(BaseModel):
    """Represents a 2D coordinate (pixel or metric pitch plane)."""
    x: float
    y: float

    def to_tuple(self) -> Tuple[float, float]:
        return (self.x, self.y)

    def to_array(self) -> np.ndarray:
        return np.array([self.x, self.y], dtype=np.float64)


class CalibrationData(BaseModel):
    """Pydantic model representing pitch calibration matrices and parameters."""
    camera_id: str = Field(default="camera_0")
    image_width: int = Field(ge=0)
    image_height: int = Field(ge=0)
    image_points: List[Point2D] = Field(description="Selected pixel points in image space")
    pitch_points: List[Point2D] = Field(description="Corresponding physical points in pitch ground space (meters)")
    homography_matrix: List[List[float]] = Field(description="3x3 Homography Matrix (Image -> Pitch)")
    inv_homography_matrix: List[List[float]] = Field(description="3x3 Inverse Homography Matrix (Pitch -> Image)")
    reprojection_error_px: float = Field(ge=0.0, description="Mean reprojection error in pixels")
    is_valid: bool = Field(default=True)
    validation_message: Optional[str] = Field(default=None)


class PitchCalibrator:
    """Computes homography calibration mapping camera pixels to ground pitch meters."""

    def __init__(self, max_reprojection_error_px: float = 5.0, min_points: int = 4):
        self.max_reprojection_error_px = max_reprojection_error_px
        self.min_points = min_points

    @staticmethod
    def get_standard_pitch_references() -> Dict[str, Point2D]:
        """Returns standard metric 2D ground coordinates for key pitch landmarks (in meters).
        Origin (0,0) is at bowler's stumps center on ground.
        Positive Y points toward batter's stumps (+20.12m).
        Positive X points to bowler's right (off-side for right-hander).
        """
        half_crease = CREASE_WIDTH_M / 2.0
        return {
            "bowler_stump_base": Point2D(x=0.0, y=0.0),
            "batter_stump_base": Point2D(x=0.0, y=STANDARD_PITCH_LENGTH_M),
            "bowler_crease_left": Point2D(x=-half_crease, y=POPPING_CREASE_DIST_M),
            "bowler_crease_right": Point2D(x=half_crease, y=POPPING_CREASE_DIST_M),
            "batter_crease_left": Point2D(x=-half_crease, y=STANDARD_PITCH_LENGTH_M - POPPING_CREASE_DIST_M),
            "batter_crease_right": Point2D(x=half_crease, y=STANDARD_PITCH_LENGTH_M - POPPING_CREASE_DIST_M),
        }

    def calibrate(
        self,
        image_points: List[Point2D],
        pitch_points: List[Point2D],
        image_size: Tuple[int, int],
        camera_id: str = "camera_0"
    ) -> CalibrationData:
        """Computes the 3x3 homography matrix from pixel points to metric pitch coordinates."""
        if len(image_points) < self.min_points or len(pitch_points) < self.min_points:
            raise ValueError(f"At least {self.min_points} point correspondences required for homography.")

        if len(image_points) != len(pitch_points):
            raise ValueError("Number of image points and pitch points must match.")

        src_pts = np.array([pt.to_tuple() for pt in image_points], dtype=np.float32)
        dst_pts = np.array([pt.to_tuple() for pt in pitch_points], dtype=np.float32)

        # Compute Homography matrix H (image_pixel -> pitch_meter)
        H, status = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 3.0)

        if H is None:
            logger.error("Failed to estimate Homography matrix.")
            return CalibrationData(
                camera_id=camera_id,
                image_width=image_size[0],
                image_height=image_size[1],
                image_points=image_points,
                pitch_points=pitch_points,
                homography_matrix=np.eye(3).tolist(),
                inv_homography_matrix=np.eye(3).tolist(),
                reprojection_error_px=999.0,
                is_valid=False,
                validation_message="Homography calculation failed (degenerate point configuration)"
            )

        # Compute inverse Homography H_inv (pitch_meter -> image_pixel)
        H_inv = np.linalg.inv(H)

        # Calculate reprojection error in pixels
        reproj_error = self.compute_reprojection_error(src_pts, dst_pts, H)

        is_valid = reproj_error <= self.max_reprojection_error_px
        val_msg = None if is_valid else f"Reprojection error {reproj_error:.2f}px exceeds limit {self.max_reprojection_error_px}px"

        logger.info(f"Calibrated camera '{camera_id}': reproj_error={reproj_error:.3f}px, valid={is_valid}")

        return CalibrationData(
            camera_id=camera_id,
            image_width=image_size[0],
            image_height=image_size[1],
            image_points=image_points,
            pitch_points=pitch_points,
            homography_matrix=H.tolist(),
            inv_homography_matrix=H_inv.tolist(),
            reprojection_error_px=reproj_error,
            is_valid=is_valid,
            validation_message=val_msg
        )

    def compute_reprojection_error(
        self, src_pixel_pts: np.ndarray, dst_pitch_pts: np.ndarray, H: np.ndarray
    ) -> float:
        """Calculates mean reprojection error in pixel space (pitch -> image -> compare pixel)."""
        H_inv = np.linalg.inv(H)

        # Transform pitch ground points back to image pixel space
        pitch_pts_reshaped = dst_pitch_pts.reshape(-1, 1, 2)
        projected_pixels = cv2.perspectiveTransform(pitch_pts_reshaped, H_inv).reshape(-1, 2)

        # Euclidean distance in pixels
        errors = np.linalg.norm(src_pixel_pts - projected_pixels, axis=1)
        return float(np.mean(errors))

    @staticmethod
    def image_to_pitch(pixel_point: Point2D, homography_matrix: Union[np.ndarray, List[List[float]]]) -> Point2D:
        """Transforms a 2D pixel coordinate (x,y) to pitch ground plane coordinate (X,Y in meters)."""
        H = np.array(homography_matrix, dtype=np.float64)
        pt_array = np.array([[[pixel_point.x, pixel_point.y]]], dtype=np.float32)
        transformed = cv2.perspectiveTransform(pt_array, H)
        tx, ty = transformed[0][0]
        return Point2D(x=float(tx), y=float(ty))

    @staticmethod
    def pitch_to_image(pitch_point: Point2D, inv_homography_matrix: Union[np.ndarray, List[List[float]]]) -> Point2D:
        """Transforms a 2D pitch ground coordinate (X,Y in meters) back to image pixel coordinate (x,y)."""
        H_inv = np.array(inv_homography_matrix, dtype=np.float64)
        pt_array = np.array([[[pitch_point.x, pitch_point.y]]], dtype=np.float32)
        transformed = cv2.perspectiveTransform(pt_array, H_inv)
        px, py = transformed[0][0]
        return Point2D(x=float(px), y=float(py))

    @staticmethod
    def save_calibration(calibration: CalibrationData, output_path: Union[str, Path]) -> Path:
        """Serializes calibration data to a JSON file."""
        path = Path(output_path).resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(calibration.model_dump_json(indent=2))
        logger.info(f"Saved calibration to {path}")
        return path

    @staticmethod
    def load_calibration(input_path: Union[str, Path]) -> CalibrationData:
        """Loads and deserializes calibration data from a JSON file."""
        path = Path(input_path).resolve()
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return CalibrationData.model_validate(data)
