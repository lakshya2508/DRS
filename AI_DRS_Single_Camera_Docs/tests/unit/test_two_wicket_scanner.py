"""
Unit tests for Two-Wicket Pitch Scanner and Dual-Anchor Pitch Calibration Engine.
"""

import pytest
from fastapi.testclient import TestClient

from ai_drs.api.main import app
from ai_drs.calibration.two_wicket_scanner import TwoWicketPitchScanner, WicketAnchor

client = TestClient(app)


def test_two_wicket_scanner_axis_calculation():
    scanner = TwoWicketPitchScanner()
    state = scanner.update_calibration()

    assert state.calibration_status == "CALIBRATED"
    assert state.wicket_a.wicket_id == "WICKET_A"
    assert state.wicket_b.wicket_id == "WICKET_B"
    assert state.pitch_axis_length_pixels > 0.0
    assert state.confidence_score >= 0.90


def test_pixel_to_pitch_coordinate_transformation():
    scanner = TwoWicketPitchScanner()

    # Transform center point
    x_m, y_m = scanner.pixel_to_pitch_coords(960.0, 920.0)
    assert isinstance(x_m, float)
    assert isinstance(y_m, float)


def test_line_and_length_classification():
    scanner = TwoWicketPitchScanner()

    # Good length, middle stump
    c1 = scanner.classify_line_and_length(pitch_x_meters=0.0, pitch_y_meters=15.0, batter_hand="RIGHT")
    assert c1.length == "GOOD_LENGTH"
    assert c1.line == "MIDDLE"

    # Yorker, outside off stump
    c2 = scanner.classify_line_and_length(pitch_x_meters=-0.3, pitch_y_meters=19.5, batter_hand="RIGHT")
    assert c2.length == "YORKER"
    assert c2.line == "OUTSIDE_OFF"

    # Bouncer, wide
    c3 = scanner.classify_line_and_length(pitch_x_meters=-0.8, pitch_y_meters=8.0, batter_hand="RIGHT")
    assert c3.length == "BOUNCER"
    assert c3.line == "WIDE"


def test_two_wicket_scanner_api_status():
    res = client.get("/api/v1/two-wicket-scanner/status")
    assert res.status_code == 200
    data = res.json()
    assert data["calibration_status"] == "CALIBRATED"
    assert data["wicket_a"]["wicket_id"] == "WICKET_A"
    assert data["wicket_b"]["wicket_id"] == "WICKET_B"


def test_two_wicket_scanner_api_update_anchors():
    payload = {
        "wicket_a_x": 960.0,
        "wicket_a_y": 900.0,
        "wicket_b_x": 960.0,
        "wicket_b_y": 200.0,
        "confidence_a": 0.98,
        "confidence_b": 0.95
    }
    res = client.post("/api/v1/two-wicket-scanner/update-anchors", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["confidence_score"] == 0.96
    assert data["pitch_axis_length_pixels"] == 700.0


def test_two_wicket_scanner_api_classify_delivery():
    payload = {
        "pitch_x_meters": 0.0,
        "pitch_y_meters": 15.0,
        "batter_hand": "RIGHT"
    }
    res = client.post("/api/v1/two-wicket-scanner/classify-delivery", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["line"] == "MIDDLE"
    assert data["length"] == "GOOD_LENGTH"
