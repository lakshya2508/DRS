"""
Match Condition Engine and Situation Classifier Module for AI DRS
"""

from typing import Optional, Tuple
from pydantic import BaseModel, Field

from ai_drs.common.config import load_yaml_config
from ai_drs.common.logging import setup_logger
from ai_drs.match.models import MatchState

logger = setup_logger("ai_drs.match.condition")


class MatchConditionPayload(BaseModel):
    """Schema representing live match condition metrics (Match Condition Panel)."""
    match_id: str
    target: Optional[int] = None
    current_score: int
    wickets_lost: int
    overs_formatted: float
    runs_required: Optional[int] = None
    balls_remaining: int
    current_run_rate: float
    required_run_rate: Optional[float] = None
    wickets_remaining: int
    projected_score: int
    partnership_runs: int
    partnership_balls: int
    situation_classification: str = Field(description="'COMFORTABLE', 'STABLE', 'PRESSURE', 'HIGH_PRESSURE', 'CRITICAL'")
    situation_description: str


class MatchConditionEngine:
    """Computes real-time match conditions, baseline projections, and situation classification."""

    def __init__(self, config_path: str = "configs/situation.yaml"):
        raw_config = load_yaml_config(config_path)
        self.thresholds = raw_config.get("situation_thresholds", {})

    def classify_situation(self, state: MatchState) -> Tuple[str, str]:
        """Classifies match situation into COMFORTABLE, STABLE, PRESSURE, HIGH_PRESSURE, or CRITICAL."""
        if state.match_status == "COMPLETED":
            return "COMPLETED", state.result_summary or "Match completed"

        # Innings 1 classification (based on wickets remaining and current run rate)
        if state.target is None:
            if state.wickets_remaining >= 7 and state.current_run_rate >= 8.0:
                return "COMFORTABLE", "Batting team in strong position"
            elif state.wickets_remaining >= 5:
                return "STABLE", "Solid batting foundation"
            elif state.wickets_remaining >= 3:
                return "PRESSURE", "Wickets falling, partnership needed"
            else:
                return "CRITICAL", "Tail-enders batting, high risk of all out"

        # Innings 2 Chase classification (based on Required Run Rate and Wickets Remaining)
        rrr = state.required_run_rate if state.required_run_rate is not None else 0.0
        w_rem = state.wickets_remaining
        runs_req = state.runs_required if state.runs_required is not None else 0

        desc = f"Need {runs_req} runs from {state.balls_remaining} balls (RRR {rrr:.2f})"

        if runs_req <= 0:
            return "COMPLETED", "Target achieved"

        if w_rem <= 1 or (rrr > 18.0 and state.balls_remaining < 18):
            return "CRITICAL", f"CRITICAL: {desc}"

        if rrr <= 6.0 and w_rem >= 7:
            return "COMFORTABLE", f"COMFORTABLE: {desc}"

        if rrr <= 9.0 and w_rem >= 5:
            return "STABLE", f"STABLE: {desc}"

        if rrr <= 13.0 and w_rem >= 3:
            return "PRESSURE", f"PRESSURE: {desc}"

        return "HIGH_PRESSURE", f"HIGH PRESSURE: {desc}"

    def compute_conditions(self, state: MatchState) -> MatchConditionPayload:
        """Computes comprehensive match conditions and baseline score projection."""
        crr = state.current_run_rate
        total_overs = state.total_overs

        # Baseline projection: Current Score + (CRR * Remaining Overs)
        remaining_overs = state.balls_remaining / 6.0
        if state.target is not None:
            projected = min(state.target, int(round(state.score + (crr * remaining_overs))))
        else:
            projected = int(round(state.score + (crr * remaining_overs)))

        sit_class, sit_desc = self.classify_situation(state)

        logger.info(
            f"Match [{state.match_id}] Conditions: Score={state.score}/{state.wickets}, "
            f"Need={state.runs_required} off {state.balls_remaining}b, Sit={sit_class}"
        )

        return MatchConditionPayload(
            match_id=state.match_id,
            target=state.target,
            current_score=state.score,
            wickets_lost=state.wickets,
            overs_formatted=state.overs_formatted,
            runs_required=state.runs_required,
            balls_remaining=state.balls_remaining,
            current_run_rate=crr,
            required_run_rate=state.required_run_rate,
            wickets_remaining=state.wickets_remaining,
            projected_score=projected,
            partnership_runs=state.partnership.runs,
            partnership_balls=state.partnership.balls,
            situation_classification=sit_class,
            situation_description=sit_desc
        )
