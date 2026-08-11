"""
Real-Time Win Probability & DLS Momentum Index Engine for Autonomous Cricket Engine
"""

from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger
from ai_drs.match.models import MatchState

logger = setup_logger("ai_drs.match.momentum")


class WinProbabilityIndex(BaseModel):
    """Schema representing real-time win probability and momentum index."""
    match_id: str
    team_a_win_pct: float = Field(ge=0.0, le=100.0)
    team_b_win_pct: float = Field(ge=0.0, le=100.0)
    momentum_shift: float = Field(description="-100.0 (Favors Team A) to +100.0 (Favors Team B)")
    favored_team: str


class MomentumEngine:
    """Calculates live in-play win probability and momentum swings."""

    @staticmethod
    def calculate_win_probability(match_state: MatchState) -> WinProbabilityIndex:
        """Calculates win probability percentage based on RRR, CRR, and wickets remaining."""
        if not match_state.is_target_set or match_state.target_runs is None:
            # First Innings Baseline
            crr = (match_state.runs / (match_state.overs + match_state.legal_balls / 6.0)) if (match_state.overs > 0 or match_state.legal_balls > 0) else 6.0
            wickets_left = 10 - match_state.wickets
            team_a_pct = min(90.0, max(10.0, 50.0 + (crr - 7.0) * 5.0 + (wickets_left - 5) * 4.0))
            team_b_pct = 100.0 - team_a_pct
        else:
            # Second Innings Target Chase
            runs_needed = match_state.target_runs - match_state.runs
            overs_left = (match_state.total_overs * 6 - (match_state.overs * 6 + match_state.legal_balls)) / 6.0

            if runs_needed <= 0:
                team_b_pct = 100.0
                team_a_pct = 0.0
            elif match_state.wickets >= 10 or overs_left <= 0:
                team_b_pct = 0.0
                team_a_pct = 100.0
            else:
                rrr = (runs_needed / overs_left) if overs_left > 0 else 99.0
                wickets_left = 10 - match_state.wickets
                # Formula: Base 50% shifted by (rrr - crr) and wickets left
                crr = (match_state.runs / (match_state.overs + match_state.legal_balls / 6.0)) if (match_state.overs > 0 or match_state.legal_balls > 0) else 6.0
                diff = crr - rrr
                team_b_pct = min(99.0, max(1.0, 50.0 + diff * 8.0 + (wickets_left - 3) * 6.0))
                team_a_pct = 100.0 - team_b_pct

        favored = match_state.team_b if team_b_pct >= 50.0 else match_state.team_a
        momentum_shift = float(team_b_pct - team_a_pct)

        logger.info(
            f"Win Probability [{match_state.match_id}]: "
            f"{match_state.team_a}={team_a_pct:.1f}%, {match_state.team_b}={team_b_pct:.1f}% (Favored: {favored})"
        )

        return WinProbabilityIndex(
            match_id=match_state.match_id,
            team_a_win_pct=round(team_a_pct, 1),
            team_b_win_pct=round(team_b_pct, 1),
            momentum_shift=round(momentum_shift, 1),
            favored_team=favored
        )
