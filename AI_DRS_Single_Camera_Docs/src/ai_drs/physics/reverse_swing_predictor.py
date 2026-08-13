"""
Ball Leather Roughness & Reverse Swing Predictor for AI DRS Physics
"""

from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.physics.reverse_swing")


class ReverseSwingPrediction(BaseModel):
    """Schema representing reverse swing trigger probability and lateral deviation forecast."""
    over_number: float
    is_reverse_swing_active: bool
    roughness_differential_ratio: float = Field(ge=1.0)
    predicted_lateral_drift_m: float
    confidence: float = Field(ge=0.0, le=1.0)


class ReverseSwingPredictor:
    """Predicts reverse swing onset based on ball age (overs), leather scuffing, and humidity."""

    @staticmethod
    def predict_reverse_swing(
        over_number: float,
        relative_humidity_pct: float = 45.0,
        ball_speed_kmh: float = 140.0
    ) -> ReverseSwingPrediction:
        """Predicts reverse swing onset (typically overs 25-40 with low humidity and high pace)."""
        # Reverse swing requires old ball (overs >= 25), low humidity (< 60%), and high pace (> 130 km/h)
        is_old_ball = over_number >= 25.0
        is_dry_air = relative_humidity_pct <= 60.0
        is_high_pace = ball_speed_kmh >= 130.0

        is_active = is_old_ball and is_dry_air and is_high_pace
        roughness_ratio = float(1.0 + min(2.5, (over_number / 15.0))) if is_active else 1.0
        drift_m = float(0.15 + (over_number - 25.0) * 0.01) if is_active else 0.0
        conf = min(0.95, max(0.50, (over_number / 35.0))) if is_active else 0.85

        if is_active:
            logger.info(
                f"Reverse Swing Active [Over {over_number:.1f}]: pace={ball_speed_kmh}km/h, "
                f"humidity={relative_humidity_pct}%, drift={drift_m:.2f}m"
            )

        return ReverseSwingPrediction(
            over_number=over_number,
            is_reverse_swing_active=is_active,
            roughness_differential_ratio=round(roughness_ratio, 2),
            predicted_lateral_drift_m=round(drift_m, 3),
            confidence=round(conf, 2)
        )
