"""
Unit tests for LBW Decision Engine Module
"""

import pytest

from ai_drs.calibration.pitch_calibration import CalibrationData, Point2D
from ai_drs.decision.lbw_engine import LBWDecisionEngine, LBWDecision, DecisionEvidence
from ai_drs.events.event_detector import PitchingEvent, ImpactEvent
from ai_drs.tracking.ball_tracker import BallTrack, TrackedPoint
from ai_drs.trajectory.trajectory_engine import TrajectoryPrediction, WicketProjection


@pytest.fixture
def mock_calibration():
    return CalibrationData(
        camera_id="cam_1",
        image_width=1280,
        image_height=720,
        image_points=[Point2D(x=0, y=0)] * 4,
        pitch_points=[Point2D(x=0, y=0)] * 4,
        homography_matrix=[[1, 0, 0], [0, 1, 0], [0, 0, 1]],
        inv_homography_matrix=[[1, 0, 0], [0, 1, 0], [0, 0, 1]],
        reprojection_error_px=0.5,
        is_valid=True
    )


@pytest.fixture
def mock_good_track():
    pts = [TrackedPoint(frame_id=i, x=640, y=500 - i * 20, confidence=0.9) for i in range(10)]
    return BallTrack(points=pts, total_frames=10, detected_count=10, coverage_ratio=1.0, track_confidence=0.9)


def test_lbw_decision_out(mock_calibration, mock_good_track):
    engine = LBWDecisionEngine()

    pitching = PitchingEvent(frame_id=3, pixel_point=Point2D(x=640, y=600), metric_point=Point2D(x=0.0, y=5.0), zone="IN_LINE", confidence=0.9)
    impact = ImpactEvent(frame_id=8, pixel_point=Point2D(x=640, y=400), metric_point=Point2D(x=0.0, y=18.5), zone="IN_LINE", confidence=0.9)
    wicket_proj = WicketProjection(projected_x_m=0.0, projected_z_m=0.35, projected_pixel=Point2D(x=640, y=300), hit_result="HITTING", hit_probability=0.9, confidence=0.9)
    trajectory = TrajectoryPrediction(fitted_points_metric=[], projected_points_metric=[], wicket_projection=wicket_proj, fit_rmse=0.01, confidence=0.9)

    decision = engine.evaluate(pitching, impact, trajectory, mock_good_track, mock_calibration)

    assert isinstance(decision, LBWDecision)
    assert decision.result == "OUT"
    assert "OUT" in decision.recommendation_reason
    assert decision.confidence > 0.8


def test_lbw_decision_not_out_pitching_outside_leg(mock_calibration, mock_good_track):
    engine = LBWDecisionEngine()

    pitching = PitchingEvent(frame_id=3, pixel_point=Point2D(x=750, y=600), metric_point=Point2D(x=0.5, y=5.0), zone="OUTSIDE_LEG", confidence=0.9)
    impact = ImpactEvent(frame_id=8, pixel_point=Point2D(x=640, y=400), metric_point=Point2D(x=0.0, y=18.5), zone="IN_LINE", confidence=0.9)
    wicket_proj = WicketProjection(projected_x_m=0.0, projected_z_m=0.35, projected_pixel=Point2D(x=640, y=300), hit_result="HITTING", hit_probability=0.9, confidence=0.9)
    trajectory = TrajectoryPrediction(fitted_points_metric=[], projected_points_metric=[], wicket_projection=wicket_proj, fit_rmse=0.01, confidence=0.9)

    decision = engine.evaluate(pitching, impact, trajectory, mock_good_track, mock_calibration)

    assert decision.result == "NOT_OUT"
    assert "Pitching outside leg" in decision.recommendation_reason


def test_lbw_decision_not_out_impact_outside_off_with_shot(mock_calibration, mock_good_track):
    engine = LBWDecisionEngine()

    pitching = PitchingEvent(frame_id=3, pixel_point=Point2D(x=640, y=600), metric_point=Point2D(x=0.0, y=5.0), zone="IN_LINE", confidence=0.9)
    impact = ImpactEvent(frame_id=8, pixel_point=Point2D(x=500, y=400), metric_point=Point2D(x=-0.5, y=18.5), zone="OUTSIDE_OFF", confidence=0.9)
    wicket_proj = WicketProjection(projected_x_m=0.0, projected_z_m=0.35, projected_pixel=Point2D(x=640, y=300), hit_result="HITTING", hit_probability=0.9, confidence=0.9)
    trajectory = TrajectoryPrediction(fitted_points_metric=[], projected_points_metric=[], wicket_projection=wicket_proj, fit_rmse=0.01, confidence=0.9)

    decision = engine.evaluate(pitching, impact, trajectory, mock_good_track, mock_calibration, shot_offered=True)

    assert decision.result == "NOT_OUT"
    assert "Impact outside off stump with shot offered" in decision.recommendation_reason


def test_lbw_decision_impact_outside_leg(mock_calibration, mock_good_track):
    engine = LBWDecisionEngine()

    pitching = PitchingEvent(frame_id=3, pixel_point=Point2D(x=640, y=600), metric_point=Point2D(x=0.0, y=5.0), zone="IN_LINE", confidence=0.9)
    impact = ImpactEvent(frame_id=8, pixel_point=Point2D(x=750, y=400), metric_point=Point2D(x=0.5, y=18.5), zone="OUTSIDE_LEG", confidence=0.9)
    wicket_proj = WicketProjection(projected_x_m=0.0, projected_z_m=0.35, projected_pixel=Point2D(x=640, y=300), hit_result="HITTING", hit_probability=0.9, confidence=0.9)
    trajectory = TrajectoryPrediction(fitted_points_metric=[], projected_points_metric=[], wicket_projection=wicket_proj, fit_rmse=0.01, confidence=0.9)

    decision = engine.evaluate(pitching, impact, trajectory, mock_good_track, mock_calibration)

    assert decision.result == "NOT_OUT"
    assert "Impact outside leg stump" in decision.recommendation_reason


def test_lbw_decision_clipping_umpires_call(mock_calibration, mock_good_track):
    engine = LBWDecisionEngine()

    pitching = PitchingEvent(frame_id=3, pixel_point=Point2D(x=640, y=600), metric_point=Point2D(x=0.0, y=5.0), zone="IN_LINE", confidence=0.9)
    impact = ImpactEvent(frame_id=8, pixel_point=Point2D(x=640, y=400), metric_point=Point2D(x=0.0, y=18.5), zone="IN_LINE", confidence=0.9)
    wicket_proj = WicketProjection(projected_x_m=0.13, projected_z_m=0.35, projected_pixel=Point2D(x=680, y=300), hit_result="CLIPPING", hit_probability=0.5, confidence=0.9)
    trajectory = TrajectoryPrediction(fitted_points_metric=[], projected_points_metric=[], wicket_projection=wicket_proj, fit_rmse=0.01, confidence=0.9)

    decision = engine.evaluate(pitching, impact, trajectory, mock_good_track, mock_calibration)

    assert decision.result == "OUT"
    assert "clip stumps" in decision.recommendation_reason


def test_lbw_decision_not_out_missing(mock_calibration, mock_good_track):
    engine = LBWDecisionEngine()

    pitching = PitchingEvent(frame_id=3, pixel_point=Point2D(x=640, y=600), metric_point=Point2D(x=0.0, y=5.0), zone="IN_LINE", confidence=0.9)
    impact = ImpactEvent(frame_id=8, pixel_point=Point2D(x=640, y=400), metric_point=Point2D(x=0.0, y=18.5), zone="IN_LINE", confidence=0.9)
    wicket_proj = WicketProjection(projected_x_m=0.50, projected_z_m=0.35, projected_pixel=Point2D(x=800, y=300), hit_result="MISSING", hit_probability=0.05, confidence=0.9)
    trajectory = TrajectoryPrediction(fitted_points_metric=[], projected_points_metric=[], wicket_projection=wicket_proj, fit_rmse=0.01, confidence=0.9)

    decision = engine.evaluate(pitching, impact, trajectory, mock_good_track, mock_calibration)

    assert decision.result == "NOT_OUT"
    assert "projected to miss" in decision.recommendation_reason


def test_lbw_decision_inconclusive_low_coverage(mock_calibration):
    engine = LBWDecisionEngine()

    pts = [TrackedPoint(frame_id=i, x=640, y=500, confidence=0.9) for i in range(3)]
    poor_track = BallTrack(points=pts, total_frames=10, detected_count=3, coverage_ratio=0.30, track_confidence=0.3)

    pitching = PitchingEvent(frame_id=3, pixel_point=Point2D(x=640, y=600), metric_point=Point2D(x=0.0, y=5.0), zone="IN_LINE", confidence=0.9)
    impact = ImpactEvent(frame_id=8, pixel_point=Point2D(x=640, y=400), metric_point=Point2D(x=0.0, y=18.5), zone="IN_LINE", confidence=0.9)
    wicket_proj = WicketProjection(projected_x_m=0.0, projected_z_m=0.35, projected_pixel=Point2D(x=640, y=300), hit_result="HITTING", hit_probability=0.9, confidence=0.9)
    trajectory = TrajectoryPrediction(fitted_points_metric=[], projected_points_metric=[], wicket_projection=wicket_proj, fit_rmse=0.01, confidence=0.9)

    decision = engine.evaluate(pitching, impact, trajectory, poor_track, mock_calibration)

    assert decision.result == "INCONCLUSIVE"
    assert "tracking coverage" in decision.recommendation_reason


def test_lbw_decision_inconclusive_bad_calibration(mock_good_track):
    engine = LBWDecisionEngine()
    invalid_calib = CalibrationData(
        camera_id="cam_1",
        image_width=1280,
        image_height=720,
        image_points=[],
        pitch_points=[],
        homography_matrix=[[1,0,0],[0,1,0],[0,0,1]],
        inv_homography_matrix=[[1,0,0],[0,1,0],[0,0,1]],
        reprojection_error_px=15.0,
        is_valid=False
    )

    decision = engine.evaluate(None, None, None, mock_good_track, invalid_calib)

    assert decision.result == "INCONCLUSIVE"
    assert "calibration" in decision.recommendation_reason
