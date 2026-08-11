"""
Pitch Wear & Environmental Friction Model for AI DRS Trajectory Physics
"""

from typing import Tuple
from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.physics.environment")


class PitchConditionState(BaseModel):
    """Schema representing pitch surface friction, bounce damping, and weather dynamics."""
    pitch_dampness_pct: float = Field(ge=0.0, le=100.0)
    grass_cover_pct: float = Field(ge=0.0, le=100.0)
    temperature_c: float = Field(default=25.0)
    relative_humidity_pct: float = Field(default=50.0)
    coefficient_of_friction_mu: float = Field(ge=0.1, le=1.0)
    coefficient_of_restitution_cor: float = Field(ge=0.3, le=0.9)


class PitchEnvironmentModel:
    """Calculates friction coefficients and bounce restitution based on pitch wear and humidity."""

    @staticmethod
    def compute_pitch_dynamics(
        dampness_pct: float = 10.0,
        grass_cover_pct: float = 20.0,
        temperature_c: float = 28.0,
        relative_humidity_pct: float = 55.0
    ) -> PitchConditionState:
        """Computes friction coefficient mu and restitution cor from pitch surface parameters."""
        # Dampness lowers friction, increases skid
        base_mu = 0.45 - (dampness_pct / 100.0) * 0.15 + (grass_cover_pct / 100.0) * 0.10
        base_cor = 0.65 - (dampness_pct / 100.0) * 0.10 + (grass_cover_pct / 100.0) * 0.08

        mu = min(0.85, max(0.20, base_mu))
        cor = min(0.85, max(0.40, base_cor))

        logger.info(
            f"Pitch Physics Dynamics: Dampness={dampness_pct}%, Grass={grass_cover_pct}% -> "
            f"Friction mu={mu:.3f}, Restitution CoR={cor:.3f}"
        )

        return PitchConditionState(
            pitch_dampness_pct=dampness_pct,
            grass_cover_pct=grass_cover_pct,
            temperature_c=temperature_c,
            relative_humidity_pct=relative_humidity_pct,
            coefficient_of_friction_mu=round(mu, 3),
            coefficient_of_restitution_cor=round(cor, 3)
        )

    def calculate_bounce_velocity(
        self,
        v_y_in: float,
        v_z_in: float,
        condition: PitchConditionState
    ) -> Tuple[float, float]:
        """Calculates post-bounce velocity components (v_y_out, v_z_out) using CoR and friction."""
        v_y_out = float(v_y_in * (1.0 - condition.coefficient_of_friction_mu * 0.15))
        v_z_out = float(abs(v_z_in) * condition.coefficient_of_restitution_cor)
        return v_y_out, v_z_out
