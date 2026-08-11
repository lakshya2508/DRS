"""
Pitch Pitching Heatmap & Line-Length Density Generator for AI DRS
"""

from typing import Dict, List, Tuple
import numpy as np
from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.analytics.heatmap")


class PitchZone(str):
    YORKER = "YORKER"
    FULL = "FULL"
    GOOD_LENGTH = "GOOD_LENGTH"
    SHORT = "SHORT"


class PitchBouncePoint(BaseModel):
    """Schema representing pitch bounce spatial coordinates."""
    x_m: float = Field(description="Lateral offset from pitch center in meters")
    y_m: float = Field(description="Distance along pitch from bowler stumps in meters (0 to 20.12m)")


class PitchHeatmapSummary(BaseModel):
    """Schema representing 2D pitch bounce density heatmap summary."""
    bowler_name: str
    total_deliveries: int
    full_pct: float
    good_length_pct: float
    short_pct: float
    yorker_pct: float
    outside_off_pct: float
    stumps_pct: float
    outside_leg_pct: float


class PitchHeatmapEngine:
    """Generates 2D pitch bounce point density maps and line/length distribution stats."""

    @staticmethod
    def classify_length(y_m: float) -> str:
        """Classifies ball pitch bounce length based on Y coordinate along pitch (20.12m total)."""
        if y_m >= 18.5:
            return "YORKER"
        elif 15.0 <= y_m < 18.5:
            return "FULL"
        elif 10.0 <= y_m < 15.0:
            return "GOOD_LENGTH"
        else:
            return "SHORT"

    @staticmethod
    def classify_line(x_m: float) -> str:
        """Classifies ball pitch line relative to stumps width (-0.114m to +0.114m)."""
        if x_m < -0.1143:
            return "OUTSIDE_OFF"
        elif -0.1143 <= x_m <= 0.1143:
            return "STUMPS"
        else:
            return "OUTSIDE_LEG"

    def generate_bowler_heatmap(
        self,
        bowler_name: str,
        bounce_points: List[PitchBouncePoint]
    ) -> PitchHeatmapSummary:
        """Computes length and line distribution percentages for a bowler."""
        total = len(bounce_points)
        if total == 0:
            return PitchHeatmapSummary(
                bowler_name=bowler_name,
                total_deliveries=0,
                full_pct=0.0,
                good_length_pct=0.0,
                short_pct=0.0,
                yorker_pct=0.0,
                outside_off_pct=0.0,
                stumps_pct=0.0,
                outside_leg_pct=0.0
            )

        lengths = [self.classify_length(pt.y_m) for pt in bounce_points]
        lines = [self.classify_line(pt.x_m) for pt in bounce_points]

        summary = PitchHeatmapSummary(
            bowler_name=bowler_name,
            total_deliveries=total,
            full_pct=float(lengths.count("FULL") / total * 100.0),
            good_length_pct=float(lengths.count("GOOD_LENGTH") / total * 100.0),
            short_pct=float(lengths.count("SHORT") / total * 100.0),
            yorker_pct=float(lengths.count("YORKER") / total * 100.0),
            outside_off_pct=float(lines.count("OUTSIDE_OFF") / total * 100.0),
            stumps_pct=float(lines.count("STUMPS") / total * 100.0),
            outside_leg_pct=float(lines.count("OUTSIDE_LEG") / total * 100.0)
        )

        logger.info(
            f"Pitch Heatmap [{bowler_name}]: {total} balls -> "
            f"GoodLength={summary.good_length_pct:.1f}%, Stumps={summary.stumps_pct:.1f}%"
        )
        return summary
