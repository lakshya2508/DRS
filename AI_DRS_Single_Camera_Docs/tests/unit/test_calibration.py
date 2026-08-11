"""
Unit tests for Camera and Pitch Homography Calibration Module
"""

import tempfile
from pathlib import Path
import numpy as np
import pytest

from ai_drs.calibration.pitch_calibration import (
    PitchCalibrator,
    CalibrationData,
    Point2D,
    STANDARD_PITCH_LENGTH_M,
)


@pytest.fixture
def synthetic_homography_points():
    """Generates synthetic 4-point correspondence representing a camera behind bowler view."""
    # 4 Pitch world ground points (meters)
    pitch_pts = [
        Point2D(x=-1.32, y=1.22),   # Bowler crease left
        Point2D(x=1.32, y=1.22),    # Bowler crease right
        Point2D(x=1.32, y=18.90),   # Batter crease right
        Point2D(x=-1.32, y=18.90),  # Batter crease left
    ]

    # Corresponding synthetic image pixel points (simulating trapezoidal perspective projection)
    image_pts = [
        Point2D(x=300.0, y=900.0),  # Bowler crease left (near, wide)
        Point2D(x=980.0, y=900.0),  # Bowler crease right (near, wide)
        Point2D(x=700.0, y=300.0),  # Batter crease right (far, narrow)
        Point2D(x=580.0, y=300.0),  # Batter crease left (far, narrow)
    ]

    return image_pts, pitch_pts


def test_standard_pitch_references():
    refs = PitchCalibrator.get_standard_pitch_references()
    assert "bowler_stump_base" in refs
    assert "batter_stump_base" in refs
    assert refs["batter_stump_base"].y == STANDARD_PITCH_LENGTH_M
    assert refs["bowler_stump_base"].x == 0.0


def test_calibrate_and_transform(synthetic_homography_points):
    image_pts, pitch_pts = synthetic_homography_points
    calibrator = PitchCalibrator(max_reprojection_error_px=5.0)

    calib = calibrator.calibrate(
        image_points=image_pts,
        pitch_points=pitch_pts,
        image_size=(1280, 720),
        camera_id="cam_behind_bowler_1"
    )

    assert isinstance(calib, CalibrationData)
    assert calib.is_valid is True
    assert calib.reprojection_error_px < 1.0  # Perfect synthetic alignment

    # Test forward transform: image pixel -> pitch meter
    pitch_res = PitchCalibrator.image_to_pitch(image_pts[0], calib.homography_matrix)
    assert abs(pitch_res.x - pitch_pts[0].x) < 0.05
    assert abs(pitch_res.y - pitch_pts[0].y) < 0.05

    # Test inverse transform: pitch meter -> image pixel
    image_res = PitchCalibrator.pitch_to_image(pitch_pts[2], calib.inv_homography_matrix)
    assert abs(image_res.x - image_pts[2].x) < 1.0
    assert abs(image_res.y - image_pts[2].y) < 1.0


def test_calibration_serialization(synthetic_homography_points):
    image_pts, pitch_pts = synthetic_homography_points
    calibrator = PitchCalibrator()
    calib = calibrator.calibrate(image_pts, pitch_pts, image_size=(1280, 720))

    with tempfile.TemporaryDirectory() as tmpdir:
        json_path = Path(tmpdir) / "calibration.json"
        saved_path = PitchCalibrator.save_calibration(calib, json_path)

        assert saved_path.exists()
        loaded_calib = PitchCalibrator.load_calibration(json_path)

        assert loaded_calib.camera_id == calib.camera_id
        assert loaded_calib.reprojection_error_px == calib.reprojection_error_px
        assert loaded_calib.homography_matrix == calib.homography_matrix


def test_insufficient_points_error():
    calibrator = PitchCalibrator(min_points=4)
    with pytest.raises(ValueError, match="At least 4 point correspondences required"):
        calibrator.calibrate(
            image_points=[Point2D(x=0, y=0), Point2D(x=1, y=1)],
            pitch_points=[Point2D(x=0, y=0), Point2D(x=1, y=1)],
            image_size=(1280, 720)
        )

    with pytest.raises(ValueError, match="Number of image points and pitch points must match"):
        calibrator.calibrate(
            image_points=[Point2D(x=0, y=0)] * 4,
            pitch_points=[Point2D(x=0, y=0)] * 5,
            image_size=(1280, 720)
        )


def test_high_reprojection_error(synthetic_homography_points):
    image_pts, pitch_pts = synthetic_homography_points
    # Add a 5th point with artificial distortion/noise in image space
    image_pts_5 = image_pts + [Point2D(x=640.0, y=600.0)]
    pitch_pts_5 = pitch_pts + [Point2D(x=2.5, y=10.0)]  # Perturbed coordinate

    calibrator = PitchCalibrator(max_reprojection_error_px=0.1)
    calib = calibrator.calibrate(image_pts_5, pitch_pts_5, image_size=(1280, 720))

    assert calib.is_valid is False
    assert "exceeds limit" in calib.validation_message


def test_point2d_methods():
    pt = Point2D(x=12.5, y=34.8)
    assert pt.to_tuple() == (12.5, 34.8)
    np.testing.assert_array_equal(pt.to_array(), np.array([12.5, 34.8]))
