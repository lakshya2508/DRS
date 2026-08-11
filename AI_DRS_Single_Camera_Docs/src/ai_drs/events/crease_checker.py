"""
Front-Foot No-Ball & Tramline Wide Ball Detection Engine for Autonomous Umpiring
"""

from typing import Optional
from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.events.crease")


class CreaseCheckResult(BaseModel):
    """Schema representing autonomous crease and wide check result."""
    is_front_foot_no_ball: bool = Field(description="True if bowler front foot toe overstepped popping crease")
    front_foot_overstep_m: float = Field(description="Overstep distance in meters (> 0.0 means overstepped)")
    is_wide_ball: bool = Field(description="True if ball bounced outside off/leg tramlines")
    wide_line_type: Optional[str] = Field(default=None, description="'OFF_SIDE_WIDE', 'LEG_SIDE_WIDE'")
    ball_lateral_x_m: float


class CreaseCheckerEngine:
    """Evaluates bowler front-foot oversteps and ball tramline wide boundaries."""

    def __init__(
        self,
        off_wide_tramline_x: float = -0.89,
        leg_wide_tramline_x: float = 0.45
    ):
        self.off_wide_tramline_x = off_wide_tramline_x
        self.leg_wide_tramline_x = leg_wide_tramline_x

    def check_front_foot_crease(self, front_toe_y_m: float) -> Tuple_bool_float := (bool, float):
        """Checks if bowler's front toe overstepped popping crease line (Y = 0.0m)."""
        overstep = float(front_toe_y_m - 0.0)
        is_no_ball = overstep > 0.005  # > 5mm overstep tolerance
        return is_no_ball, overstep

    def check_wide_tramline(self, ball_x_m: float, batter_stance_rhb: bool = True) -> Tuple_bool_opt := (bool, Optional[str]):
        """Checks if ball passed outside off-side or leg-side tramlines."""
        if ball_x_m < self.off_wide_tramline_x:
            return True, "OFF_SIDE_WIDE"
        elif ball_x_m > self.leg_wide_tramline_x:
            return True, "LEG_SIDE_WIDE"
        return False, None

    def evaluate_delivery_legality(
        self,
        front_toe_y_m: float,
        ball_bounce_x_m: float,
        batter_stance_rhb: bool = True
    ) -> CreaseCheckResult:
        """Evaluates delivery front-foot overstep and tramline wide status."""
        is_no_ball, overstep = self.check_front_foot_crease(front_toe_y_m)
        is_wide, wide_type = self.check_wide_tramline(ball_bounce_x_m, batter_stance_rhb)

        if is_no_ball:
            logger.info(f"AUTONOMOUS UMPIRE: NO BALL DETECTED! Overstep={overstep * 100.0:.1f}cm")
        if is_wide:
            logger.info(f"AUTONOMOUS UMPIRE: WIDE BALL DETECTED! Type={wide_type}, X={ball_bounce_x_m:.2f}m")

        return CreaseCheckResult(
            is_front_foot_no_ball=is_no_ball,
            front_foot_overstep_m=round(overstep, 3),
            is_wide_ball=is_wide,
            wide_line_type=wide_type,
            ball_lateral_x_m=round(ball_bounce_x_m, 3)
        )
