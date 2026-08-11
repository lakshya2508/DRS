"""
Unit tests for Pitching and Impact Event Detection Module
"""

import pytest

from ai_drs.calibration.pitch_calibration import PitchCalibrator, Point2D
from ai_drs.events.event_detector import (
    EventDetector,
    PitchingEvent,
    ImpactEvent,
)
from ai_drs.tracking.ball_tracker import BallTrack, TrackedPoint


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


@pytest.fixture
def synthetic_bounce_track():
    """Generates synthetic delivery ball track moving towards batter (y decreases in image)."""
    points = []
    for i in range(16):
        # Y in image decreases from 800 to 320 as ball moves toward batter stumps
        py = 800.0 - i * 30.0
        px = 640.0
        points.append(
            TrackedPoint(
                frame_id=i,
                x=px,
                y=py,
                confidence=0.9,
                is_interpolated=False
            )
        )
    return BallTrack(points=points, start_frame=0, end_frame=15, total_frames=16)


def test_zone_classification():
    detector = EventDetector()
    # Stumps between -0.1143m and +0.1143m
    assert detector.classify_zone(0.0, "RHB") == "IN_LINE"
    assert detector.classify_zone(-0.05, "RHB") == "IN_LINE"
    assert detector.classify_zone(+0.05, "RHB") == "IN_LINE"

    assert detector.classify_zone(-0.50, "RHB") == "OUTSIDE_OFF"
    assert detector.classify_zone(+0.50, "RHB") == "OUTSIDE_LEG"

    # Left handed batter
    assert detector.classify_zone(-0.50, "LHB") == "OUTSIDE_LEG"
    assert detector.classify_zone(+0.50, "LHB") == "OUTSIDE_OFF"


def test_detect_pitching(synthetic_bounce_track, mock_calibration):
    detector = EventDetector()
    pitching = detector.detect_pitching(synthetic_bounce_track, calibration=mock_calibration)

    assert pitching is not None
    assert isinstance(pitching, PitchingEvent)
    assert pitching.zone == "IN_LINE"
    assert pitching.confidence > 0.7


def test_detect_impact(synthetic_bounce_track, mock_calibration):
    detector = EventDetector()
    pad_bbox = (630.0, 310.0, 650.0, 330.0)  # Near frame 15 position (py=350.0)

    impact = detector.detect_impact(
        synthetic_bounce_track,
        calibration=mock_calibration,
        pad_bbox=pad_bbox
    )

    assert impact is not None
    assert isinstance(impact, ImpactEvent)
    assert impact.frame_id == 15
    assert impact.zone == "IN_LINE"
    assert impact.confidence > 0.7


def test_short_track_event_detection():
    detector = EventDetector()
    short_track = BallTrack(points=[TrackedPoint(frame_id=0, x=10, y=10, confidence=0.8)])

    assert detector.detect_pitching(short_track) is None
    assert detector.detect_impact(short_track) is None
    assert detector.detect_pitching(None) is None
