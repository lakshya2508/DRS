"""
Unit tests for Physics Calibration & Trajectory Tuning Engine Module
"""

import pytest

from ai_drs.calibration.stereo_calibration import Point3D
from ai_drs.physics.physics_tuner import PhysicsTrajectoryTuner, PhysicsTunedTrajectory


def test_physics_trajectory_tuner():
    tuner = PhysicsTrajectoryTuner()

    pts = [
        Point3D(x=0.05, y=14.0, z=0.0),
        Point3D(x=0.03, y=16.0, z=0.3),
        Point3D(x=0.01, y=18.0, z=0.5),
    ]

    traj = tuner.fit_and_extrapolate_trajectory(pts, target_y=20.12)

    assert isinstance(traj, PhysicsTunedTrajectory)
    assert traj.tracked_points_count == 3
    assert traj.projected_wicket_y == 20.12
    assert isinstance(traj.projected_wicket_x, float)
    assert isinstance(traj.projected_wicket_z, float)
    assert traj.fit_residual_m < 0.05


def test_insufficient_points_trajectory():
    tuner = PhysicsTrajectoryTuner()
    with pytest.raises(ValueError):
        tuner.fit_and_extrapolate_trajectory([Point3D(x=0, y=10, z=1)])
