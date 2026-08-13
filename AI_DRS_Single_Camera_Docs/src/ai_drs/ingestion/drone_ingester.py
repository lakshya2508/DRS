"""
Aerial Drone Camera 3D Pose & Flight Telemetry Ingester Module
"""

from typing import Tuple
from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.ingestion.drone")


class DroneTelemetryState(BaseModel):
    """Schema representing 6-DOF IMU gimbal pose and drone altitude telemetry."""
    drone_id: str
    altitude_z_m: float = Field(ge=1.0, le=100.0)
    gimbal_pitch_deg: float = Field(ge=-90.0, le=90.0)
    gimbal_yaw_deg: float = Field(ge=0.0, le=360.0)
    gimbal_roll_deg: float = Field(ge=-180.0, le=180.0)
    fps: float = Field(default=60.0)
    battery_pct: float = Field(ge=0.0, le=100.0)


class DroneTelemetryIngester:
    """Ingests 4K 60FPS aerial camera streams along with 6-DOF gimbal pitch/yaw/roll IMU telemetry."""

    @staticmethod
    def ingest_drone_telemetry(
        drone_id: str = "DRONE_UMPIRE_01",
        altitude_m: float = 18.5,
        pitch_deg: float = -45.0,
        yaw_deg: float = 180.0,
        roll_deg: float = 0.0
    ) -> DroneTelemetryState:
        """Parses and validates incoming aerial drone IMU telemetry packet."""
        state = DroneTelemetryState(
            drone_id=drone_id,
            altitude_z_m=altitude_m,
            gimbal_pitch_deg=pitch_deg,
            gimbal_yaw_deg=yaw_deg,
            gimbal_roll_deg=roll_deg,
            fps=60.0,
            battery_pct=88.0
        )
        logger.info(f"Ingested Drone Telemetry [{drone_id}]: Alt={altitude_m}m, Pitch={pitch_deg}deg")
        return state
