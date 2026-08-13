"""
Wagon Wheel Shot Direction Estimator Module for AI DRS
"""

from enum import Enum
import math
from typing import Dict, List
from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.analytics.wagon_wheel")


class ShotZone(str, Enum):
    FINE_LEG = "FINE_LEG"
    SQUARE_LEG = "SQUARE_LEG"
    MIDWICKET = "MIDWICKET"
    LONG_ON = "LONG_ON"
    LONG_OFF = "LONG_OFF"
    COVER = "COVER"
    POINT = "POINT"
    THIRD_MAN = "THIRD_MAN"


class WagonWheelShot(BaseModel):
    """Schema representing a single shot on the Wagon Wheel."""
    delivery_id: str
    batter_name: str
    runs: int = Field(ge=0)
    angle_deg: float = Field(ge=0.0, le=360.0)
    distance_m: float = Field(ge=0.0)
    zone: ShotZone


class WagonWheelEngine:
    """Estimates shot trajectory angle and classifies cricket ground zones."""

    @staticmethod
    def classify_zone(angle_deg: float) -> ShotZone:
        """Maps polar angle (0 deg = Straight down ground) to 8 cricket fielding sectors."""
        deg = angle_deg % 360.0

        if 0.0 <= deg < 45.0:
            return ShotZone.LONG_ON
        elif 45.0 <= deg < 90.0:
            return ShotZone.MIDWICKET
        elif 90.0 <= deg < 135.0:
            return ShotZone.SQUARE_LEG
        elif 135.0 <= deg < 180.0:
            return ShotZone.FINE_LEG
        elif 180.0 <= deg < 225.0:
            return ShotZone.THIRD_MAN
        elif 225.0 <= deg < 270.0:
            return ShotZone.POINT
        elif 270.0 <= deg <= 315.0:
            return ShotZone.COVER
        else:
            return ShotZone.LONG_OFF


    def compute_shot(
        self,
        delivery_id: str,
        batter_name: str,
        dx_m: float,
        dy_m: float,
        runs: int
    ) -> WagonWheelShot:
        """Computes polar angle and distance from 2D displacement vector (dx, dy)."""
        distance = math.sqrt(dx_m**2 + dy_m**2)
        angle_rad = math.atan2(dx_m, dy_m)
        angle_deg = math.degrees(angle_rad) % 360.0
        zone = self.classify_zone(angle_deg)

        logger.info(
            f"Wagon Wheel Shot [{delivery_id}]: batter={batter_name}, runs={runs}, "
            f"angle={angle_deg:.1f}deg, dist={distance:.1f}m -> {zone.value}"
        )

        return WagonWheelShot(
            delivery_id=delivery_id,
            batter_name=batter_name,
            runs=runs,
            angle_deg=angle_deg,
            distance_m=distance,
            zone=zone
        )

    def summarize_batter_wagon_wheel(self, shots: List[WagonWheelShot]) -> Dict[str, int]:
        """Summarizes total runs scored per zone for a batter."""
        summary: Dict[str, int] = {z.value: 0 for z in ShotZone}
        for shot in shots:
            summary[shot.zone.value] += shot.runs
        return summary
