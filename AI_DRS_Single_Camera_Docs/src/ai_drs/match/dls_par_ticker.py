"""
Live DLS Par Score Ticker Engine for Rain Interrupted Chases
"""

import math
from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger
from ai_drs.match.dls_engine import DLSEngine

logger = setup_logger("ai_drs.match.dls_par")


class DLSParScoreTickerState(BaseModel):
    """Schema representing live DLS par score ticker state during second innings."""
    overs_bowled: float
    current_wickets: int
    current_runs: int
    par_score_runs: int
    ahead_or_behind_by_runs: int
    winning_team_if_stoppage: str


class DLSParScoreTickerEngine:
    """Computes real-time DLS Par Score for Team B during second-innings chase."""

    @classmethod
    def calculate_par_score_ticker(
        cls,
        team_a_runs: int,
        overs_bowled: float,
        current_wickets: int,
        current_runs: int,
        total_overs: float = 20.0
    ) -> DLSParScoreTickerState:
        """Calculates live par score for second-innings chase."""
        overs_rem = max(0.0, total_overs - overs_bowled)
        r1_pct = DLSEngine.get_resource_percentage(total_overs, 0)
        r2_rem_pct = DLSEngine.get_resource_percentage(overs_rem, current_wickets)

        r2_used_pct = r1_pct - r2_rem_pct

        if r1_pct > 0:
            par_score = int(math.floor(team_a_runs * (r2_used_pct / r1_pct)))
        else:
            par_score = 0

        diff = current_runs - par_score
        winner = "TEAM_B" if diff >= 0 else "TEAM_A"

        logger.debug(f"DLS Par Ticker ({overs_bowled} ov, {current_wickets} wkts): Par={par_score}, Score={current_runs} -> {winner}")

        return DLSParScoreTickerState(
            overs_bowled=overs_bowled,
            current_wickets=current_wickets,
            current_runs=current_runs,
            par_score_runs=par_score,
            ahead_or_behind_by_runs=diff,
            winning_team_if_stoppage=winner
        )
