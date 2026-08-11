"""
Unit tests for Magnus Effect & Wind Vector Aerodynamic Simulator Module
"""

import pytest

from ai_drs.physics.wind_aerodynamics import (
    AerodynamicSimulator,
    AerodynamicVectorState,
)


def test_aerodynamic_simulator_magnus_effect():
    sim = AerodynamicSimulator()
    aero = sim.compute_aerodynamic_forces(
        velocity_xyz=(1.0, 35.0, -2.0),
        spin_rpm=2400.0,
        seam_angle_deg=20.0,
        crosswind_x_m_s=3.0
    )

    assert isinstance(aero, AerodynamicVectorState)
    assert aero.crosswind_velocity_x_m_s == 3.0
    assert abs(aero.magnus_lateral_accel_x) > 0.0
    assert abs(aero.magnus_vertical_accel_z) > 0.0
