"""
DLS 4.0 Revised Target Score Recalculator for Rain Interrupted Matches
"""

import math
from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger
from ai_drs.match.dls_engine import DLSEngine

logger = setup_logger("ai_drs.match.dls_target")


class DLSTargetResult(BaseModel):
    """Schema representing recalculated DLS target score for rain-affected match."""
    team_a_runs: int
    team_a_resources_pct: float
    team_b_resources_pct: float
    revised_target_runs: int
    overs_allocated_team_b: float


class DLSTargetCalculator:
    """Calculates revised target score T2 for Team B when rain interrupts play."""

    G50_T20 = 160.0  # Standard average T20 total
    G50_ODI = 245.0  # Standard average ODI total

    @classmethod
    def calculate_revised_target(
        self,
        team_a_runs: int,
        team_a_resources_pct: float,
        team_b_resources_pct: float,
        is_t20: bool = True
    ) -> DLSTargetResult:
        """Calculates DLS target score T2 = S + 1 when Team 2 resources R2 differ from R1."""
        g50 = self.G50_T20 if is_t20 else self.G50_ODI

        if team_b_resources_pct == team_a_resources_pct:
            target = team_a_runs + 1
        elif team_b_resources_pct < team_a_resources_pct:
            # Team B has less resources
            target = int(math.floor(team_a_runs * (team_b_resources_pct / team_a_resources_pct))) + 1
        else:
            # Team B has more resources
            target = int(math.floor(team_a_runs + (team_b_resources_pct - team_a_resources_pct) * (g50 / 100.0))) + 1

        logger.info(
            f"DLS Revised Target Calculated: Team A={team_a_runs} (R1={team_a_resources_pct}%) -> "
            f"Team B Target={target} (R2={team_b_resources_pct}%)"
        )

        return DLSTargetResult(
            team_a_runs=team_a_runs,
            team_a_resources_pct=team_a_resources_pct,
            team_b_resources_pct=team_b_resources_pct,
            revised_target_runs=target,
            overs_allocated_team_b=20.0 if is_t20 else 50.0
        )
