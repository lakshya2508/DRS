"""
Unit tests for Multi-Camera 3D Stereoscopic Fusion and Calibration Module
"""

import numpy as np
import pytest

from ai_drs.calibration.pitch_calibration import Point2D
from ai_drs.calibration.stereo_calibration import (
    CameraExtrinsics,
    Point3D,
    StereoCalibrator,
)
from ai_drs.trajectory.stereo_fusion import (
    MultiCameraFusionEngine,
    TriangulatedPoint3D,
)


def test_stereo_calibration_dlt():
    # Define 6 known 3D spatial points
    world_pts = [
        Point3D(x=-1.32, y=1.22, z=0.0),
        Point3D(x=1.32, y=1.22, z=0.0),
        Point3D(x=1.32, y=20.12, z=0.0),
        Point3D(x=-1.32, y=20.12, z=0.0),
        Point3D(x=0.0, y=10.0, z=1.5),
        Point3D(x=0.5, y=15.0, z=2.0),
    ]

    # Ground truth synthetic 3x4 projection matrix P
    P_gt = np.array([
        [800.0, 0.0, 640.0, -100.0],
        [0.0, 800.0, 360.0, -200.0],
        [0.0, 0.0, 1.0, 10.0]
    ], dtype=np.float64)

    image_pts = []
    for wpt in world_pts:
        X_h = np.array([wpt.x, wpt.y, wpt.z, 1.0])
        proj = P_gt @ X_h
        image_pts.append(Point2D(x=proj[0] / proj[2], y=proj[1] / proj[2]))

    calib = StereoCalibrator.compute_projection_matrix(image_pts, world_pts)

    assert isinstance(calib, CameraExtrinsics)
    assert calib.is_valid is True
    assert calib.reprojection_error_px < 0.1


def test_multicam_triangulation_and_track_fusion():
    # 2 Synthetic cameras
    P1 = [
        [1000.0, 0.0, 640.0, 0.0],
        [0.0, 1000.0, 360.0, 0.0],
        [0.0, 0.0, 1.0, 0.0]
    ]

    P2 = [
        [1000.0, 0.0, 640.0, -500.0],
        [0.0, 1000.0, 360.0, 0.0],
        [0.0, 0.0, 1.0, 0.0]
    ]

    # Ground truth 3D point (X=0.5m, Y=10.0m, Z=1.2m)
    X_gt = np.array([0.5, 10.0, 1.2, 1.0])

    proj1 = np.array(P1) @ X_gt
    u1, v1 = proj1[0] / proj1[2], proj1[1] / proj1[2]

    proj2 = np.array(P2) @ X_gt
    u2, v2 = proj2[0] / proj2[2], proj2[1] / proj2[2]

    img_pts = [Point2D(x=u1, y=v1), Point2D(x=u2, y=v2)]

    tri_pt = MultiCameraFusionEngine.triangulate_3d_point([P1, P2], img_pts, frame_id=1)

    assert isinstance(tri_pt, TriangulatedPoint3D)
    assert pytest.approx(tri_pt.point3d.x, abs=1e-3) == 0.5
    assert pytest.approx(tri_pt.point3d.y, abs=1e-3) == 10.0
    assert pytest.approx(tri_pt.point3d.z, abs=1e-3) == 1.2
    assert tri_pt.reprojection_residual_px < 1e-4

    # Test Track Fusion
    calib1 = CameraExtrinsics(camera_id="C1", projection_matrix=P1, reprojection_error_px=0.0)
    calib2 = CameraExtrinsics(camera_id="C2", projection_matrix=P2, reprojection_error_px=0.0)

    track1 = [Point2D(x=u1, y=v1)]
    track2 = [Point2D(x=u2, y=v2)]

    engine = MultiCameraFusionEngine()
    fused_traj = engine.fuse_camera_tracks([calib1, calib2], [track1, track2])

    assert len(fused_traj) == 1
    assert pytest.approx(fused_traj[0].point3d.x, abs=1e-3) == 0.5
