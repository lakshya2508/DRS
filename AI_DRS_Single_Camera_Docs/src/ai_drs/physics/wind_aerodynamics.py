"""
Magnus Effect & Wind Vector Aerodynamic Simulator for AI DRS Flight Path
"""

import math
from typing import Tuple
from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.physics.wind")


class AerodynamicVectorState(BaseModel):
    """Schema representing aerodynamic forces and crosswind acceleration vectors."""
    crosswind_velocity_x_m_s: float
    headwind_velocity_y_m_s: float
    air_density_rho: float = Field(default=1.225, description="Air density in kg/m^3")
    magnus_lateral_accel_x: float
    magnus_vertical_accel_z: float


class AerodynamicSimulator:
    """Simulates Magnus effect seam swing and crosswind aerodynamic forces on cricket ball trajectory."""

    def __init__(self, ball_mass_kg: float = 0.160, ball_radius_m: float = 0.036):
        self.mass = ball_mass_kg
        self.radius = ball_radius_m
        self.area = math.pi * (ball_radius_m ** 2)

    def compute_aerodynamic_forces(
        self,
        velocity_xyz: Tuple[float, float, float],
        spin_rpm: float = 1200.0,
        seam_angle_deg: float = 15.0,
        crosswind_x_m_s: float = 2.0,
        headwind_y_m_s: float = 0.0,
        air_density_rho: float = 1.225
    ) -> AerodynamicVectorState:
        """Calculates Magnus lateral acceleration and wind drag force vectors."""
        vx, vy, vz = velocity_xyz
        v_speed = math.sqrt(vx**2 + vy**2 + vz**2)

        # Lift Coefficient Cl via Magnus effect spin parameter
        omega_rad_s = (spin_rpm * 2.0 * math.pi) / 60.0
        spin_param = (omega_rad_s * self.radius) / max(0.1, v_speed)
        cl = float(0.25 * spin_param * math.sin(math.radians(seam_angle_deg)))

        # Magnus acceleration: F = 0.5 * rho * v^2 * A * Cl
        magnus_force = 0.5 * air_density_rho * (v_speed ** 2) * self.area * cl
        magnus_accel_x = float((magnus_force * math.cos(math.radians(seam_angle_deg))) / self.mass)
        magnus_accel_z = float((magnus_force * math.sin(math.radians(seam_angle_deg))) / self.mass)

        logger.debug(
            f"Aerodynamic Magnus Simulator: spin={spin_rpm}rpm, seam={seam_angle_deg}deg -> "
            f"Magnus Accel X={magnus_accel_x:.3f}m/s^2, Z={magnus_accel_z:.3f}m/s^2"
        )

        return AerodynamicVectorState(
            crosswind_velocity_x_m_s=crosswind_x_m_s,
            headwind_velocity_y_m_s=headwind_y_m_s,
            air_density_rho=air_density_rho,
            magnus_lateral_accel_x=round(magnus_accel_x, 3),
            magnus_vertical_accel_z=round(magnus_accel_z, 3)
        )
