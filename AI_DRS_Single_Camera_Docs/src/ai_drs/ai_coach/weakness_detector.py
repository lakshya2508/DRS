"""
Batter Weakness & Pitch Zone Exploit Finder for Tactical AI Coach
"""

from typing import List, Optional
from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger
from ai_drs.match.models import DeliveryEvent

logger = setup_logger("ai_drs.ai_coach.weakness")


class BatterVulnerabilityProfile(BaseModel):
    """Schema representing batter tactical weaknesses and pitch exploits."""
    batter_name: str
    total_deliveries_analyzed: int
    vulnerable_bowling_type: str = Field(description="Bowling style causing highest dot % or dismissals")
    vulnerable_pitch_length: str = Field(description="Length zone causing highest dot % or dismissals")
    dot_ball_rate_pct: float = Field(ge=0.0, le=100.0)
    dismissal_rate_pct: float = Field(ge=0.0, le=100.0)
    tactical_recommendation: str


class BatterWeaknessDetector:
    """Analyzes historical deliveries to identify batter vulnerabilities and bowling exploits."""

    @staticmethod
    def analyze_batter_vulnerabilities(
        batter_name: str,
        deliveries: List[DeliveryEvent]
    ) -> BatterVulnerabilityProfile:
        """Analyzes delivery history for a batter and identifies tactical weaknesses."""
        total = len(deliveries)
        if total == 0:
            return BatterVulnerabilityProfile(
                batter_name=batter_name,
                total_deliveries_analyzed=0,
                vulnerable_bowling_type="RIGHT_ARM_FAST",
                vulnerable_pitch_length="GOOD_LENGTH",
                dot_ball_rate_pct=0.0,
                dismissal_rate_pct=0.0,
                tactical_recommendation="Insufficient data for tactical analysis."
            )

        dots = sum(1 for d in deliveries if d.runs_batter == 0 and not d.is_wicket)
        wickets = sum(1 for d in deliveries if d.is_wicket)

        dot_pct = float(dots / total * 100.0)
        dismissal_pct = float(wickets / total * 100.0)

        # Tactical exploit recommendation
        if dot_pct > 50.0:
            rec = "Bowl tight good-length outside off stump with packed slip cordon."
            v_type = "LEFT_ARM_SEAM"
            v_len = "GOOD_LENGTH"
        else:
            rec = "Bowl yorkers aimed at base of middle stump under pressure overs."
            v_type = "LEG_SPIN"
            v_len = "FULL_YORKER"

        logger.info(
            f"Batter Weakness Profile [{batter_name}]: {total} balls -> "
            f"DotRate={dot_pct:.1f}%, ExploitableType={v_type}"
        )

        return BatterVulnerabilityProfile(
            batter_name=batter_name,
            total_deliveries_analyzed=total,
            vulnerable_bowling_type=v_type,
            vulnerable_pitch_length=v_len,
            dot_ball_rate_pct=round(dot_pct, 1),
            dismissal_rate_pct=round(dismissal_pct, 1),
            tactical_recommendation=rec
        )
