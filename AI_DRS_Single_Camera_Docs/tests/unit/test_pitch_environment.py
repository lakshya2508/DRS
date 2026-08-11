"""
Unit tests for Pitch Wear & Environmental Friction Model Module
"""

import pytest

from ai_drs.physics.pitch_environment import (
    PitchConditionState,
    PitchEnvironmentModel,
)


def test_pitch_environment_model_computation():
    model = PitchEnvironmentModel()
    cond = model.compute_pitch_dynamics(dampness_pct=20.0, grass_cover_pct=30.0)

    assert isinstance(cond, PitchConditionState)
    assert 0.20 <= cond.coefficient_of_friction_mu <= 0.85
    assert 0.40 <= cond.coefficient_of_restitution_cor <= 0.85

    v_y_out, v_z_out = model.calculate_bounce_velocity(v_y_in=25.0, v_z_in=-8.0, condition=cond)
    assert v_y_out < 25.0
    assert v_z_out > 0.0
