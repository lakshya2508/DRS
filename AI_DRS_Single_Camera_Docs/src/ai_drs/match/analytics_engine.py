"""
Match Analytics & Projection Engine Module for AI DRS
"""

from typing import List, Optional, Set
import numpy as np
from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger
from ai_drs.match.models import MatchState

logger = setup_logger("ai_drs.match.analytics")


class ProjectionRange(BaseModel):
    """Score projection range (conservative, expected, aggressive)."""
    min_projected_score: int
    expected_projected_score: int
    max_projected_score: int


class OverRunRatePoint(BaseModel):
    """Over-by-over run rate data point."""
    over_number: int
    cumulative_score: int
    over_runs: int
    run_rate: float


class WicketTimelineEvent(BaseModel):
    """Timeline event representing a fallen wicket."""
    wicket_number: int
    score: int
    overs_formatted: float
    player_name: str
    dismissal_info: str


class MatchAnalyticsPayload(BaseModel):
    """Schema representing complete match intelligence analytics."""
    match_id: str
    run_rate_trend: List[OverRunRatePoint] = Field(default_factory=list)
    wicket_timeline: List[WicketTimelineEvent] = Field(default_factory=list)
    pressure_trend: List[float] = Field(default_factory=list, description="Pressure index (0 to 100) per over")
    score_projection: ProjectionRange


class ProjectionEngine:
    """Computes baseline score projections (conservative, expected, aggressive)."""

    @staticmethod
    def compute_projection(state: MatchState) -> ProjectionRange:
        """Calculates min, expected, and max projected scores based on CRR and wickets in hand."""
        crr = state.current_run_rate if state.current_run_rate > 0 else 6.0
        rem_overs = state.balls_remaining / 6.0

        w_factor = state.wickets_remaining / 10.0

        # Conservative: CRR - 2.0 (min 3.0)
        min_rr = max(3.0, crr - 2.0)
        # Aggressive: CRR + 3.0 * (wickets_remaining / 10)
        max_rr = crr + (3.0 * w_factor)

        exp_proj = int(round(state.score + (crr * rem_overs)))
        min_proj = int(round(state.score + (min_rr * rem_overs)))
        max_proj = int(round(state.score + (max_rr * rem_overs)))

        if state.target is not None:
            exp_proj = min(state.target, exp_proj)
            min_proj = min(state.target, min_proj)
            max_proj = min(state.target, max_proj)

        return ProjectionRange(
            min_projected_score=min_proj,
            expected_projected_score=exp_proj,
            max_projected_score=max_proj
        )


class MatchAnalyticsEngine:
    """Generates match trends, wicket timelines, and pressure indexes from MatchState history."""

    def __init__(self):
        self.projection_engine = ProjectionEngine()

    def generate_analytics(self, state_history: List[MatchState]) -> Optional[MatchAnalyticsPayload]:
        """Generates analytics payload from sequential MatchState snapshots."""
        if not state_history:
            return None

        current_state = state_history[-1]
        run_rate_trend: List[OverRunRatePoint] = []
        wicket_timeline: List[WicketTimelineEvent] = []
        pressure_trend: List[float] = []

        seen_wickets: Set[int] = set()
        seen_overs: Set[int] = set()

        for idx, state in enumerate(state_history):
            if state.total_legal_balls > 0 and state.total_legal_balls % 6 == 0:
                over_num = state.total_legal_balls // 6
                if over_num not in seen_overs:
                    seen_overs.add(over_num)

                    # End of over checkpoint
                    rr = round(state.score / (state.total_legal_balls / 6.0), 2)
                    run_rate_trend.append(
                        OverRunRatePoint(
                            over_number=over_num,
                            cumulative_score=state.score,
                            over_runs=state.current_over_runs,
                            run_rate=rr
                        )
                    )

                    # Pressure Index (0-100) based on RRR / CRR ratio or wickets lost
                    if state.target:
                        rrr = state.required_run_rate or 0.0
                        press = min(100.0, max(0.0, (rrr / max(1.0, rr)) * 40.0 + (10 - state.wickets_remaining) * 6.0))
                    else:
                        press = min(100.0, max(0.0, (10 - state.wickets_remaining) * 8.0 + max(0.0, 10.0 - rr) * 3.0))
                    pressure_trend.append(round(press, 1))

            # Track wicket timeline
            if state.wickets > 0 and state.wickets not in seen_wickets:
                seen_wickets.add(state.wickets)
                wicket_timeline.append(
                    WicketTimelineEvent(
                        wicket_number=state.wickets,
                        score=state.score,
                        overs_formatted=state.overs_formatted,
                        player_name=state.striker.name,
                        dismissal_info=state.striker.dismissal_info or "Out"
                    )
                )

        proj = self.projection_engine.compute_projection(current_state)

        logger.info(
            f"Generated Match Analytics [{current_state.match_id}]: "
            f"trend_len={len(run_rate_trend)}, wickets={len(wicket_timeline)}, "
            f"expected_proj={proj.expected_projected_score}"
        )

        return MatchAnalyticsPayload(
            match_id=current_state.match_id,
            run_rate_trend=run_rate_trend,
            wicket_timeline=wicket_timeline,
            pressure_trend=pressure_trend,
            score_projection=proj
        )
