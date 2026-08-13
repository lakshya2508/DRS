"""
Unit tests for Ball Bounce Deviation & Rough Spot Predictor Module
"""

import pytest

from ai_drs.analytics.pitch_curator_scanner import PitchHealthReport
from ai_drs.physics.bounce_deviation_predictor import (
    BounceDeviationPrediction,
    BounceDeviationPredictorEngine,
)


def test_bounce_deviation_predictor():
    report = PitchHealthReport(moisture_pct=10.0, grass_coverage_pct=20.0, max_crack_width_mm=4.5)
    pred = BounceDeviationPredictorEngine.predict_bounce_deviation(landing_y_m=12.5, health=report, over_number=42.0)

    assert isinstance(pred, BounceDeviationPrediction)
    assert pred.pitch_y_landing_m == 12.5
    assert pred.is_unpredictable_spot is True
    assert pred.deviation_vertical_delta_z_m > 0.0
