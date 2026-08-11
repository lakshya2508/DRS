"""
Unit tests for Ball Tracker Module
"""

import pytest

from ai_drs.detection.ball_detector import BallDetection
from ai_drs.tracking.ball_tracker import (
    KalmanBallTracker,
    BallTrack,
    TrackedPoint,
)


@pytest.fixture
def synthetic_delivery_detections():
    """Generates a synthetic linear ball trajectory over 20 frames with slight noise."""
    frame_dets = []
    # Ball moving from (100, 200) to (700, 500) over 20 frames
    for i in range(20):
        frame_id = i
        cx = 100.0 + i * 30.0
        cy = 200.0 + i * 15.0
        det = BallDetection(
            frame_id=frame_id,
            bbox=(cx - 10, cy - 10, cx + 10, cy + 10),
            center=(cx, cy),
            radius=10.0,
            confidence=0.85
        )
        frame_dets.append((frame_id, [det]))
    return frame_dets


def test_track_continuous_sequence(synthetic_delivery_detections):
    tracker = KalmanBallTracker()
    track = tracker.track_sequence(synthetic_delivery_detections, track_id="delivery_1")

    assert track is not None
    assert isinstance(track, BallTrack)
    assert track.track_id == "delivery_1"
    assert len(track.points) == 20
    assert track.detected_count == 20
    assert track.interpolated_count == 0
    assert track.coverage_ratio == 1.0
    assert track.track_confidence > 0.8

    # Verify positions smooth properly
    assert abs(track.points[0].x - 100.0) < 1.0
    assert abs(track.points[-1].x - 670.0) < 5.0


def test_track_with_occlusion(synthetic_delivery_detections):
    # Simulate occlusion by removing detections for frames 8, 9, 10
    occluded_dets = []
    for f_id, dets in synthetic_delivery_detections:
        if f_id in (8, 9, 10):
            occluded_dets.append((f_id, []))
        else:
            occluded_dets.append((f_id, dets))

    tracker = KalmanBallTracker(max_missed_frames=5)
    track = tracker.track_sequence(occluded_dets, track_id="delivery_occluded")

    assert track is not None
    assert len(track.points) == 20
    assert track.detected_count == 17
    assert track.interpolated_count == 3
    assert track.points[8].is_interpolated is True
    assert track.points[9].is_interpolated is True
    assert track.points[10].is_interpolated is True


def test_outlier_rejection():
    tracker = KalmanBallTracker(gating_threshold_px=50.0)
    dets = []
    for i in range(10):
        cx = 100.0 + i * 20.0
        cy = 200.0
        det = BallDetection(
            frame_id=i,
            bbox=(cx - 5, cy - 5, cx + 5, cy + 5),
            center=(cx, cy),
            radius=5.0,
            confidence=0.9
        )
        if i == 5:
            # Outlier detection 300px away
            outlier = BallDetection(
                frame_id=i,
                bbox=(cx + 300, cy, cx + 310, cy + 10),
                center=(cx + 300.0, cy),
                radius=5.0,
                confidence=0.9
            )
            dets.append((i, [outlier]))
        else:
            dets.append((i, [det]))

    track = tracker.track_sequence(dets)
    assert track is not None
    # Outlier should be rejected and point interpolated
    assert track.points[5].is_interpolated is True
    assert abs(track.points[5].x - (100.0 + 5 * 20.0)) < 15.0


def test_short_track_rejection():
    tracker = KalmanBallTracker(min_track_length=5)
    short_dets = [
        (0, [BallDetection(frame_id=0, bbox=(0,0,10,10), center=(5,5), radius=5, confidence=0.8)]),
        (1, [BallDetection(frame_id=1, bbox=(10,10,20,20), center=(15,15), radius=5, confidence=0.8)]),
    ]
    track = tracker.track_sequence(short_dets)
    assert track is None


def test_empty_sequence():
    tracker = KalmanBallTracker()
    track = tracker.track_sequence([])
    assert track is None
