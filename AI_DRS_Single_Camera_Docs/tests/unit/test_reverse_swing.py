"""
Unit tests for Ball Leather Roughness & Reverse Swing Predictor Module
"""

import pytest

from ai_drs.physics.reverse_swing_predictor import (
    ReverseSwingPrediction,
    ReverseSwingPredictor,
)


def test_reverse_swing_active():
    pred = ReverseSwingPredictor.predict_reverse_swing(
        over_number=30.0, relative_humidity_pct=40.0, ball_speed_kmh=142.0
    )

    assert isinstance(pred, ReverseSwingPrediction)
    assert pred.is_reverse_swing_active is True
    assert pred.predicted_lateral_drift_m > 0.10
    assert pred.roughness_differential_ratio > 1.0


def test_reverse_swing_inactive_new_ball():
    pred = ReverseSwingPredictor.predict_reverse_swing(
        over_number=5.0, relative_humidity_pct=40.0, ball_speed_kmh=142.0
    )
    assert pred.is_reverse_swing_active is False
    assert pred.predicted_lateral_drift_m == 0.0
