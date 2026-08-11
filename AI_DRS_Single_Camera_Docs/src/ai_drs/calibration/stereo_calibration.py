"""
Multi-Camera Stereoscopic Calibration Module for AI DRS (3D Projection Matrix & DLT)
"""

from typing import List, Optional, Tuple
import numpy as np
from pydantic import BaseModel, Field

from ai_drs.calibration.pitch_calibration import Point2D
from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.calibration.stereo")


class Point3D(BaseModel):
    """Schema representing 3D metric spatial coordinates (X, Y, Z in meters)."""
    x: float
    y: float
    z: float

    def to_numpy(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z], dtype=np.float64)


class CameraExtrinsics(BaseModel):
    """Camera extrinsics and 3x4 projection matrix P."""
    camera_id: str
    projection_matrix: List[List[float]] = Field(description="3x4 DLT projection matrix P = K[R|t]")
    reprojection_error_px: float = Field(ge=0.0)
    is_valid: bool = True


class StereoCalibrator:
    """Computes 3D camera projection matrices using Direct Linear Transform (DLT)."""

    @staticmethod
    def compute_projection_matrix(
        image_points: List[Point2D], world_points: List[Point3D]
    ) -> CameraExtrinsics:
        """Solves DLT A*P = 0 for 3x4 projection matrix P using SVD."""
        if len(image_points) < 6 or len(world_points) < 6:
            raise ValueError("DLT 3D camera calibration requires at least 6 non-coplanar point correspondences.")

        num_pts = len(image_points)
        A = np.zeros((2 * num_pts, 12), dtype=np.float64)

        for i in range(num_pts):
            u, v = image_points[i].x, image_points[i].y
            X, Y, Z = world_points[i].x, world_points[i].y, world_points[i].z

            A[2 * i] = [X, Y, Z, 1, 0, 0, 0, 0, -u * X, -u * Y, -u * Z, -u]
            A[2 * i + 1] = [0, 0, 0, 0, X, Y, Z, 1, -v * X, -v * Y, -v * Z, -v]

        # Singular Value Decomposition (SVD)
        _, _, Vh = np.linalg.svd(A)
        P = Vh[-1].reshape((3, 4))

        # Normalize P matrix
        if P[2, 3] != 0:
            P = P / P[2, 3]

        # Calculate reprojection error
        total_err = 0.0
        for i in range(num_pts):
            X_h = np.array([world_points[i].x, world_points[i].y, world_points[i].z, 1.0])
            proj = P @ X_h
            if proj[2] != 0:
                u_p, v_p = proj[0] / proj[2], proj[1] / proj[2]
                err = np.sqrt((u_p - image_points[i].x)**2 + (v_p - image_points[i].y)**2)
                total_err += err

        avg_err = total_err / num_pts
        is_valid = (avg_err <= 5.0)

        logger.info(f"Calibrated 3D Camera Projection: DLT error={avg_err:.3f}px, valid={is_valid}")

        return CameraExtrinsics(
            camera_id="cam_stereo_dlt",
            projection_matrix=P.tolist(),
            reprojection_error_px=float(avg_err),
            is_valid=is_valid
        )
