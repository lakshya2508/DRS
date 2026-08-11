"""
Bowler Tactical Field Setting Recommendation Engine for AI Coach
"""

from typing import List
from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.ai_coach.field")


class FieldPosition(BaseModel):
    """Schema representing a 2D fielding position on the cricket ground."""
    position_name: str
    angle_deg: float = Field(ge=0.0, le=360.0)
    distance_m: float = Field(ge=0.0)
    is_boundary_fielder: bool = False


class TacticalFieldSetting(BaseModel):
    """Schema representing recommended 9-player field setting configuration."""
    tactical_plan_name: str
    catchers_count: int
    boundary_fielders_count: int
    field_positions: List[FieldPosition] = Field(default_factory=list)


class FieldRecommenderEngine:
    """Recommends 9-player fielding positions based on batter tendencies and match situation."""

    @staticmethod
    def recommend_field_setting(
        situation_badge: str = "PRESSURE",
        batter_primary_zone: str = "COVER"
    ) -> TacticalFieldSetting:
        """Generates 9-player field position coordinates tailored to batter stroke zones."""
        if situation_badge in ("HIGH_PRESSURE", "CRITICAL"):
            plan_name = "ATTACKING_SLIP_CORDON"
            catchers = 3
            boundary = 3
            positions = [
                FieldPosition(position_name="First Slip", angle_deg=200.0, distance_m=12.0, is_boundary_fielder=False),
                FieldPosition(position_name="Second Slip", angle_deg=210.0, distance_m=13.0, is_boundary_fielder=False),
                FieldPosition(position_name="Gully", angle_deg=225.0, distance_m=15.0, is_boundary_fielder=False),
                FieldPosition(position_name="Cover", angle_deg=290.0, distance_m=25.0, is_boundary_fielder=False),
                FieldPosition(position_name="Mid-off", angle_deg=340.0, distance_m=30.0, is_boundary_fielder=False),
                FieldPosition(position_name="Mid-on", angle_deg=20.0, distance_m=30.0, is_boundary_fielder=False),
                FieldPosition(position_name="Deep Midwicket", angle_deg=65.0, distance_m=65.0, is_boundary_fielder=True),
                FieldPosition(position_name="Deep Fine Leg", angle_deg=145.0, distance_m=65.0, is_boundary_fielder=True),
                FieldPosition(position_name="Deep Cover", angle_deg=300.0, distance_m=65.0, is_boundary_fielder=True),
            ]
        else:
            plan_name = "BALANCED_CONTAINMENT"
            catchers = 1
            boundary = 5
            positions = [
                FieldPosition(position_name="First Slip", angle_deg=200.0, distance_m=12.0, is_boundary_fielder=False),
                FieldPosition(position_name="Cover Point", angle_deg=270.0, distance_m=25.0, is_boundary_fielder=False),
                FieldPosition(position_name="Mid-off", angle_deg=340.0, distance_m=30.0, is_boundary_fielder=False),
                FieldPosition(position_name="Mid-on", angle_deg=20.0, distance_m=30.0, is_boundary_fielder=False),
                FieldPosition(position_name="Deep Midwicket", angle_deg=65.0, distance_m=65.0, is_boundary_fielder=True),
                FieldPosition(position_name="Long-on", angle_deg=15.0, distance_m=70.0, is_boundary_fielder=True),
                FieldPosition(position_name="Long-off", angle_deg=345.0, distance_m=70.0, is_boundary_fielder=True),
                FieldPosition(position_name="Deep Point", angle_deg=250.0, distance_m=65.0, is_boundary_fielder=True),
                FieldPosition(position_name="Deep Fine Leg", angle_deg=145.0, distance_m=65.0, is_boundary_fielder=True),
            ]

        logger.info(f"Recommended Field Setting [{plan_name}]: catchers={catchers}, boundary_fielders={boundary}")
        return TacticalFieldSetting(
            tactical_plan_name=plan_name,
            catchers_count=catchers,
            boundary_fielders_count=boundary,
            field_positions=positions
        )
