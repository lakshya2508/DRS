"""
Ball Bounce Deviation & Rough Spot Predictor Module
"""

from typing import Tuple
from pydantic import BaseModel, Field

from ai_drs.analytics.pitch_curator_scanner import PitchHealthReport
from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.physics.bounce_deviation")


class BounceDeviationPrediction(BaseModel):
    """Schema representing predicted ball bounce height variance and lateral seam deviation off rough spots."""
    pitch_y_landing_m: float
    expected_bounce_height_z_m: float
    deviation_vertical_delta_z_m: float
    deviation_lateral_delta_x_m: float
    is_unpredictable_spot: bool


class BounceDeviationPredictorEngine:
    """Predicts unpredictable variable bounce (delta Y/Z) and lateral seam deviation (delta X) off rough footmark spots."""

    @staticmethod
    def predict_bounce_deviation(
        landing_y_m: float,
        health: PitchHealthReport,
        over_number: float = 40.0
    ) -> BounceDeviationPrediction:
        """Calculates expected bounce height and deviation delta based on pitch crack width and match overs."""
        # Unpredictable bounce triggers when crack width > 3.0mm or late in match (over > 30)
        unpredictable = (health.max_crack_width_mm > 3.0) or (over_number > 35.0)

        delta_z = float(0.08 * (health.max_crack_width_mm / 2.0)) if unpredictable else 0.01
        delta_x = float(0.05 * (over_number / 50.0)) if unpredictable else 0.005

        logger.info(f"Bounce Deviation Prediction [Y={landing_y_m}m]: DeltaZ={delta_z*100:.1f}cm, DeltaX={delta_x*100:.1f}cm")

        return BounceDeviationPrediction(
            pitch_y_landing_m=landing_y_m,
            expected_bounce_height_z_m=0.72 + delta_z,
            deviation_vertical_delta_z_m=round(delta_z, 3),
            deviation_lateral_delta_x_m=round(delta_x, 3),
            is_unpredictable_spot=unpredictable
        )
