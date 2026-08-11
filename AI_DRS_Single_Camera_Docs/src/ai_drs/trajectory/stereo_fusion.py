"""
Multi-Camera 3D Stereoscopic Fusion & Triangulation Engine for AI DRS
"""

from typing import List, Optional
import numpy as np
from pydantic import BaseModel, Field

from ai_drs.calibration.pitch_calibration import Point2D
from ai_drs.calibration.stereo_calibration import CameraExtrinsics, Point3D
from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.trajectory.stereo")


class TriangulatedPoint3D(BaseModel):
    """Schema representing a triangulated 3D spatial trajectory point."""
    frame_id: int = Field(ge=0)
    point3d: Point3D
    reprojection_residual_px: float = Field(ge=0.0)
    participating_cameras: int = Field(ge=2)


class MultiCameraFusionEngine:
    """Fuses multi-camera 2D tracks into 3D spatial trajectories via SVD DLT triangulation."""

    @staticmethod
    def triangulate_3d_point(
        projection_matrices: List[List[List[float]]],
        image_points: List[Point2D],
        frame_id: int = 0
    ) -> TriangulatedPoint3D:
        """Triangulates a 3D point (X, Y, Z) from 2+ camera 2D observations using SVD DLT."""
        num_cams = len(projection_matrices)
        if num_cams < 2 or len(image_points) < 2:
            raise ValueError("3D Stereoscopic triangulation requires at least 2 camera views.")

        A = np.zeros((2 * num_cams, 4), dtype=np.float64)

        for i in range(num_cams):
            P = np.array(projection_matrices[i], dtype=np.float64)
            u, v = image_points[i].x, image_points[i].y

            A[2 * i] = u * P[2] - P[0]
            A[2 * i + 1] = v * P[2] - P[1]

        # Solve linear system A * X = 0 using SVD
        _, _, Vh = np.linalg.svd(A)
        X_h = Vh[-1]

        if X_h[3] != 0:
            X_h = X_h / X_h[3]

        x_3d, y_3d, z_3d = float(X_h[0]), float(X_h[1]), float(X_h[2])

        # Compute reprojection residual error
        residuals = []
        for i in range(num_cams):
            P = np.array(projection_matrices[i], dtype=np.float64)
            proj = P @ X_h
            if proj[2] != 0:
                u_p, v_p = proj[0] / proj[2], proj[1] / proj[2]
                res = np.sqrt((u_p - image_points[i].x)**2 + (v_p - image_points[i].y)**2)
                residuals.append(res)

        avg_residual = float(np.mean(residuals)) if residuals else 0.0

        logger.debug(
            f"Triangulated 3D Point [Frame {frame_id}]: ({x_3d:.3f}m, {y_3d:.3f}m, {z_3d:.3f}m), "
            f"Residual={avg_residual:.3f}px across {num_cams} cams"
        )

        return TriangulatedPoint3D(
            frame_id=frame_id,
            point3d=Point3D(x=x_3d, y=y_3d, z=z_3d),
            reprojection_residual_px=avg_residual,
            participating_cameras=num_cams
        )

    def fuse_camera_tracks(
        self,
        camera_calibrations: List[CameraExtrinsics],
        tracks_by_camera: List[List[Point2D]]
    ) -> List[TriangulatedPoint3D]:
        """Fuses synchronized 2D ball tracks from multiple cameras into a 3D spatial trajectory."""
        num_cams = len(camera_calibrations)
        if num_cams != len(tracks_by_camera):
            raise ValueError("Number of calibrations must match number of camera track lists.")

        min_len = min(len(t) for t in tracks_by_camera)
        projections = [calib.projection_matrix for calib in camera_calibrations]

        triangulated_trajectory: List[TriangulatedPoint3D] = []

        for frame_idx in range(min_len):
            img_pts = [tracks_by_camera[c][frame_idx] for c in range(num_cams)]
            pt3d = self.triangulate_3d_point(projections, img_pts, frame_id=frame_idx)
            triangulated_trajectory.append(pt3d)

        logger.info(
            f"Fused {len(triangulated_trajectory)} 3D trajectory points across {num_cams} cameras."
        )
        return triangulated_trajectory
