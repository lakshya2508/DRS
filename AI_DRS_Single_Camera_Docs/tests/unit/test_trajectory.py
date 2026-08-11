"""
Unit tests for Trajectory Engine and Wicket Projection Module
"""

import pytest

from ai_drs.calibration.pitch_calibration import PitchCalibrator, Point2D
from ai_drs.events.event_detector import PitchingEvent, ImpactEvent
from ai_drs.tracking.ball_tracker import BallTrack, TrackedPoint
from ai_drs.trajectory.trajectory_engine import (
    TrajectoryEngine,
    TrajectoryPrediction,
    WicketProjection,
    STANDARD_WICKET_Y_M,
)


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
def synthetic_hitting_track():
    """Generates synthetic track aimed straight down pitch centerline (X=0.0)."""
    points = []
    for i in range(10):
        # Ball moving from Y=5m to Y=18m at X=640 (pixel center)
        py = 700.0 - i * 35.0
        px = 640.0
        points.append(
            TrackedPoint(
                frame_id=i + 5,
                x=px,
                y=py,
                confidence=0.9,
                is_interpolated=False
            )
        )
    return BallTrack(points=points, start_frame=5, end_frame=14, total_frames=10, track_confidence=0.9)


def test_classify_wicket_intersection():
    engine = TrajectoryEngine()

    res_hitting, prob_hitting = engine.classify_wicket_intersection(0.0, 0.35)
    assert res_hitting == "HITTING"
    assert prob_hitting > 0.7

    res_missing, prob_missing = engine.classify_wicket_intersection(0.50, 0.35)
    assert res_missing == "MISSING"
    assert prob_missing < 0.2

    res_clipping, prob_clipping = engine.classify_wicket_intersection(0.13, 0.35)
    assert res_clipping == "CLIPPING"
    assert prob_clipping == 0.50


def test_predict_trajectory_hitting(synthetic_hitting_track, mock_calibration):
    engine = TrajectoryEngine()
    pitching = PitchingEvent(
        frame_id=5,
        pixel_point=Point2D(x=640.0, y=700.0),
        metric_point=Point2D(x=0.0, y=5.0),
        zone="IN_LINE",
        confidence=0.9
    )

    pred = engine.predict_trajectory(
        track=synthetic_hitting_track,
        pitching_event=pitching,
        calibration=mock_calibration
    )

    assert pred is not None
    assert isinstance(pred, TrajectoryPrediction)
    assert pred.wicket_projection.hit_result == "HITTING"
    assert pred.wicket_projection.target_y_m == STANDARD_WICKET_Y_M
    assert abs(pred.wicket_projection.projected_x_m) < 0.10
    assert len(pred.projected_points_metric) == 5
    assert pred.fit_rmse >= 0.0


def test_predict_trajectory_missing(mock_calibration):
    # Track veering far off to the side (X increasing rapidly)
    points = [
        TrackedPoint(frame_id=i, x=640.0 + i * 40.0, y=800.0 - i * 40.0, confidence=0.9)
        for i in range(10)
    ]
    track = BallTrack(points=points, start_frame=0, end_frame=9, total_frames=10, track_confidence=0.9)

    engine = TrajectoryEngine()
    pred = engine.predict_trajectory(track=track, calibration=mock_calibration)

    assert pred is not None
    assert pred.wicket_projection.hit_result == "MISSING"
    assert abs(pred.wicket_projection.projected_x_m) > 0.30


def test_short_track_trajectory():
    engine = TrajectoryEngine()
    short_track = BallTrack(points=[TrackedPoint(frame_id=0, x=10, y=10, confidence=0.8)])

    assert engine.predict_trajectory(short_track) is None
    assert engine.predict_trajectory(None) is None
