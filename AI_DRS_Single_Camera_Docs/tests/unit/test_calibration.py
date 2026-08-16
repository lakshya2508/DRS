"""
Unit tests for AutoCalibrator — camera-to-pitch geometry calibration.
"""

import numpy as np
import pytest
from fastapi.testclient import TestClient

from ai_drs.api.main import app
from ai_drs.calibration.auto_calibrator import (
    AutoCalibrator, CalibrationPoints, CalibrationResult
)

client = TestClient(app)


def test_manual_calibration_basic():
    cal = AutoCalibrator()
    points = CalibrationPoints(
        batter_crease_left  = (560.0, 520.0),
        batter_crease_right = (720.0, 520.0),
        off_stump_base      = (672.0, 510.0),
        leg_stump_base      = (608.0, 510.0),
    )
    result = cal.calibrate_from_points(points, 1280, 720)
    assert result.is_calibrated is True
    assert result.stump_left_x < result.stump_right_x
    assert result.crease_y > result.popping_y
    assert result.pixels_per_metre_x > 0


def test_manual_calibration_stump_width():
    cal = AutoCalibrator()
    points = CalibrationPoints(
        batter_crease_left  = (500.0, 600.0),
        batter_crease_right = (780.0, 600.0),
        off_stump_base      = (700.0, 580.0),
        leg_stump_base      = (580.0, 580.0),
    )
    result = cal.calibrate_from_points(points)
    # stump width should be ~120 pixels — real width 22.86cm → ~524 px/m
    assert 400 < result.pixels_per_metre_x < 700


def test_auto_calibration_synthetic_frame():
    cal   = AutoCalibrator()
    frame = np.full((720, 1280, 3), (34, 139, 34), dtype=np.uint8)
    # Draw synthetic crease lines
    import cv2
    cv2.line(frame, (400, 520), (880, 520), (255,255,255), 4)
    cv2.line(frame, (400, 280), (880, 280), (255,255,255), 4)
    result = cal.auto_calibrate_from_frame(frame)
    # May or may not find lines depending on Hough — should not crash
    assert isinstance(result, CalibrationResult)


def test_get_pitch_geometry():
    cal = AutoCalibrator()
    points = CalibrationPoints(
        batter_crease_left  = (560.0, 520.0),
        batter_crease_right = (720.0, 520.0),
        off_stump_base      = (672.0, 510.0),
        leg_stump_base      = (608.0, 510.0),
    )
    cal.calibrate_from_points(points)
    geom = cal.get_pitch_geometry()
    assert "stump_left_x" in geom
    assert "stump_right_x" in geom
    assert "crease_y" in geom
    assert "popping_y" in geom


def test_calibration_save_and_load(tmp_path):
    cal = AutoCalibrator()
    points = CalibrationPoints(
        batter_crease_left  = (560.0, 520.0),
        batter_crease_right = (720.0, 520.0),
        off_stump_base      = (672.0, 510.0),
        leg_stump_base      = (608.0, 510.0),
    )
    cal.calibrate_from_points(points)
    path = str(tmp_path / "calibration.json")
    cal.save(path)

    cal2 = AutoCalibrator()
    result = cal2.load(path)
    assert result.is_calibrated is True
    assert result.stump_left_x == cal.result.stump_left_x


# ── API Tests ──────────────────────────────────────────────────────────────

def test_api_manual_calibration():
    res = client.post("/api/v1/calibration/manual",
        params={
            "batter_crease_left_x": 560, "batter_crease_left_y": 520,
            "batter_crease_right_x": 720, "batter_crease_right_y": 520,
            "off_stump_x": 672, "off_stump_y": 510,
            "leg_stump_x": 608, "leg_stump_y": 510,
        }
    )
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["calibration"]["is_calibrated"] is True


def test_api_get_current_calibration():
    res = client.get("/api/v1/calibration/current")
    assert res.status_code == 200
    data = res.json()
    assert "calibration" in data
    assert "pitch_geometry" in data


def test_api_reset_calibration():
    res = client.post("/api/v1/calibration/reset")
    assert res.status_code == 200
    assert res.json()["status"] == "reset"
