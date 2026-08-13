"""
Unit tests for Aerial 3D Pitch Homography & Ground Surface Tracking Module
"""

import pytest

from ai_drs.calibration.aerial_homography import AerialHomographyResult, AerialPitchHomographyEngine
from ai_drs.ingestion.drone_ingester import DroneTelemetryState


def test_aerial_homography():
    telemetry = DroneTelemetryState(
        drone_id="DRONE_TEST", altitude_z_m=20.0, gimbal_pitch_deg=-60.0, gimbal_yaw_deg=180.0, gimbal_roll_deg=0.0, fps=60.0, battery_pct=90.0
    )

    res = AerialPitchHomographyEngine.compute_aerial_homography(telemetry)

    assert isinstance(res, AerialHomographyResult)
    assert res.drone_id == "DRONE_TEST"
    assert res.is_valid_homography is True
    assert res.homography_reprojection_error_m < 0.01
