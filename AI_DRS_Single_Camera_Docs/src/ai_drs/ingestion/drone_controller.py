"""
Autonomous Umpire Drone Target Tracking Controller Module
"""

from typing import Tuple
from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.ingestion.drone_controller")


class DroneControlCommand(BaseModel):
    """Schema representing autonomous drone flight waypoint command."""
    target_waypoint_xyz: Tuple[float, float, float]
    target_pitch_deg: float
    target_yaw_deg: float
    is_aligned_with_crease: bool


class AutonomousDroneController:
    """Controls drone flight trajectory to automatically track bowler release and batter popping crease."""

    @staticmethod
    def compute_tracking_command(
        bowler_y_m: float = 0.0,
        batter_y_m: float = 20.12,
        current_drone_z_m: float = 18.5
    ) -> DroneControlCommand:
        """Calculates optimal flight waypoint and gimbal angles to maintain bird's-eye view of delivery."""
        # Position drone overhead midpoint of pitch
        midpoint_y = (bowler_y_m + batter_y_m) / 2.0
        waypoint = (0.0, midpoint_y, current_drone_z_m)

        # Gimbal pointing down towards crease
        pitch_cmd = -65.0
        yaw_cmd = 180.0

        logger.info(f"Computed Autonomous Drone Command: Waypoint={waypoint}, Pitch={pitch_cmd}deg")

        return DroneControlCommand(
            target_waypoint_xyz=waypoint,
            target_pitch_deg=pitch_cmd,
            target_yaw_deg=yaw_cmd,
            is_aligned_with_crease=True
        )
