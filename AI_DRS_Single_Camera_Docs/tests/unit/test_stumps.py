"""
Unit tests for Stump and Wicket Geometry Detection Module
"""

import numpy as np
import cv2
import pytest

from ai_drs.calibration.pitch_calibration import PitchCalibrator, Point2D
from ai_drs.detection.stump_detector import (
    StumpDetector,
    WicketGeometry,
    StumpDetection,
    STUMP_WIDTH_TOTAL_M,
    STUMP_HEIGHT_M,
)


@pytest.fixture
def synthetic_stump_frame():
    """Generates synthetic image containing 3 vertical white stump lines on green background."""
    height, width = 720, 1280
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    frame[:] = (40, 100, 40)

    # Draw 3 vertical white lines simulating stumps at X=615, 640, 665, Y from 300 to 450
    cv2.line(frame, (615, 300), (615, 450), (255, 255, 255), 4)
    cv2.line(frame, (640, 300), (640, 450), (255, 255, 255), 4)
    cv2.line(frame, (665, 300), (665, 450), (255, 255, 255), 4)
    return frame


@pytest.fixture
def mock_calibration():
    pitch_pts = [
        Point2D(x=-1.32, y=1.22),
        Point2D(x=1.32, y=1.22),
        Point2D(x=1.32, y=20.12),
        Point2D(x=-1.32, y=20.12),
    ]
    image_pts = [
        Point2D(x=300.0, y=900.0),
        Point2D(x=980.0, y=900.0),
        Point2D(x=700.0, y=300.0),
        Point2D(x=580.0, y=300.0),
    ]
    calibrator = PitchCalibrator()
    return calibrator.calibrate(image_pts, pitch_pts, image_size=(1280, 720))


def test_stump_detection_with_calibration(synthetic_stump_frame, mock_calibration):
    detector = StumpDetector()
    wicket = detector.detect_stumps(synthetic_stump_frame, calibration=mock_calibration)

    assert isinstance(wicket, WicketGeometry)
    assert wicket.is_valid is True
    assert len(wicket.stumps) == 3
    assert wicket.stumps[0].stump_name == "off"
    assert wicket.stumps[1].stump_name == "middle"
    assert wicket.stumps[2].stump_name == "leg"
    assert wicket.confidence > 0.85


def test_classical_stump_detection(synthetic_stump_frame):
    detector = StumpDetector()
    wicket = detector.detect_stumps(synthetic_stump_frame, calibration=None)

    assert isinstance(wicket, WicketGeometry)
    assert wicket.is_valid is True
    assert len(wicket.stumps) == 3
    assert abs(wicket.stumps[1].base_pixel.x - 640.0) < 20.0


def test_empty_frame_stump_detection():
    blank = np.zeros((720, 1280, 3), dtype=np.uint8)
    detector = StumpDetector()

    wicket = detector.detect_stumps(blank, calibration=None)
    assert wicket.is_valid is False
    assert wicket.confidence == 0.0

    none_wicket = detector.detect_stumps(None)
    assert none_wicket.is_valid is False


def test_wicket_geometry_defaults():
    wicket = WicketGeometry()
    assert wicket.stump_width_m == STUMP_WIDTH_TOTAL_M
    assert wicket.stump_height_m == STUMP_HEIGHT_M
    assert wicket.wicket_y_m == 20.12
