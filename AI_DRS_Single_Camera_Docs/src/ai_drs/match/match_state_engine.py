"""
Authoritative MatchState Engine for AI DRS
"""

from typing import Optional
from ai_drs.common.logging import setup_logger
from ai_drs.match.models import (
    BatsmanStats,
    BowlerStats,
    DeliveryEvent,
    MatchState,
    PartnershipStats,
    TossState,
)

logger = setup_logger("ai_drs.match.engine")


class MatchStateEngine:
    """Authoritative State Engine driving all match scoreboard, player statistics, and run rate calculations."""

    @staticmethod
    def initialize_match(
        match_id: str,
        team_a: str,
        team_b: str,
        striker_name: str,
        non_striker_name: str,
        bowler_name: str,
        total_overs: int = 20,
        target: Optional[int] = None,
        toss: Optional[TossState] = None
    ) -> MatchState:
        """Initializes a new MatchState instance."""
        batting_team = toss.batting_team if toss else team_a
        bowling_team = toss.bowling_team if toss else team_b

        striker = BatsmanStats(name=striker_name)
        non_striker = BatsmanStats(name=non_striker_name)
        bowler = BowlerStats(name=bowler_name)
        partnership = PartnershipStats(batsman_1=striker_name, batsman_2=non_striker_name)

        balls_remaining = total_overs * 6
        req_rr = round(target / total_overs, 2) if (target and total_overs > 0) else None

        logger.info(f"Initialized Match [{match_id}]: {team_a} vs {team_b}, Target={target}")

        return MatchState(
            match_id=match_id,
            team_a=team_a,
            team_b=team_b,
            total_overs=total_overs,
            innings=2 if target is not None else 1,
            batting_team=batting_team,
            bowling_team=bowling_team,
            score=0,
            wickets=0,
            total_legal_balls=0,
            target=target,
            striker=striker,
            non_striker=non_striker,
            bowler=bowler,
            partnership=partnership,
            current_run_rate=0.0,
            required_run_rate=req_rr,
            runs_required=target if target else None,
            balls_remaining=balls_remaining,
            wickets_remaining=10,
            toss=toss,
            match_status="IN_PROGRESS"
        )

    def apply_delivery(self, state: MatchState, delivery: DeliveryEvent) -> MatchState:
        """Applies a validated delivery event and returns updated authoritative MatchState."""
        if state.match_status == "COMPLETED":
            logger.warning(f"Match [{state.match_id}] is already COMPLETED. Delivery ignored.")
            return state

        # 1. Total Runs Calculation
        total_runs = (
            delivery.runs_off_bat +
            delivery.wide_runs +
            delivery.noball_runs +
            delivery.bye_runs +
            delivery.legbye_runs
        )
        is_legal = (delivery.wide_runs == 0 and delivery.noball_runs == 0)

        # 2. Match Scoreboard Update
        state.score += total_runs
        state.current_over_runs += total_runs
        if is_legal:
            state.total_legal_balls += 1
            state.balls_remaining = max(0, (state.total_overs * 6) - state.total_legal_balls)

        # Format delivery text summary
        deliv_code = f"{total_runs}"
        if delivery.is_wicket:
            deliv_code = "W"
        elif delivery.wide_runs > 0:
            deliv_code = f"{delivery.wide_runs}WD"
        elif delivery.noball_runs > 0:
            deliv_code = f"{delivery.noball_runs}NB"
        state.current_over_deliveries.append(deliv_code)

        # 3. Striker Stats Update
        if delivery.wide_runs == 0:
            state.striker.balls += 1

        state.striker.runs += delivery.runs_off_bat
        if delivery.runs_off_bat == 0 and is_legal:
            state.striker.dots += 1
        elif delivery.runs_off_bat == 1:
            state.striker.ones += 1
        elif delivery.runs_off_bat == 2:
            state.striker.twos += 1
        elif delivery.runs_off_bat == 3:
            state.striker.threes += 1
        elif delivery.runs_off_bat == 4:
            state.striker.fours += 1
        elif delivery.runs_off_bat == 6:
            state.striker.sixes += 1
        state.striker.update_metrics()

        # 4. Bowler Stats Update
        bowler_conceded = delivery.runs_off_bat + delivery.wide_runs + delivery.noball_runs
        state.bowler.runs_conceded += bowler_conceded
        if is_legal:
            state.bowler.legal_balls += 1
            if total_runs == 0:
                state.bowler.dot_balls += 1

        if delivery.ball_speed_kmh is not None:
            state.bowler.speeds_kmh.append(delivery.ball_speed_kmh)
        state.bowler.update_metrics()

        # 5. Partnership Update
        state.partnership.runs += total_runs
        if is_legal:
            state.partnership.balls += 1

        # 6. Wicket Fall Update
        if delivery.is_wicket:
            state.wickets += 1
            state.wickets_remaining = max(0, 10 - state.wickets)
            if delivery.wicket_type != "RUN_OUT":
                state.bowler.wickets += 1
            state.bowler.update_metrics()

            state.striker.is_out = True
            w_type = delivery.wicket_type or "OUT"
            state.striker.dismissal_info = f"{w_type} b {delivery.bowler_name}"

            if delivery.new_batsman_name:
                state.striker = BatsmanStats(name=delivery.new_batsman_name)
                state.partnership = PartnershipStats(
                    batsman_1=state.striker.name,
                    batsman_2=state.non_striker.name
                )

        # 7. Strike Rotation (Odd running runs)
        running_runs = delivery.runs_off_bat + delivery.bye_runs + delivery.legbye_runs
        if running_runs % 2 == 1 and not delivery.is_wicket:
            state.striker, state.non_striker = state.non_striker, state.striker

        # 8. Over End Processing
        if is_legal and state.total_legal_balls % 6 == 0:
            # Over completed: rotate strike
            state.striker, state.non_striker = state.non_striker, state.striker
            state.current_over_runs = 0
            state.current_over_deliveries = []

        # 9. Run Rates and Target Chase Status
        overs_elapsed = state.total_legal_balls / 6.0
        if overs_elapsed > 0:
            state.current_run_rate = round(state.score / overs_elapsed, 2)

        if state.target is not None:
            state.runs_required = max(0, state.target - state.score)
            overs_rem = state.balls_remaining / 6.0
            if overs_rem > 0:
                state.required_run_rate = round(state.runs_required / overs_rem, 2)
            else:
                state.required_run_rate = 0.0

            # Chase completion checks
            if state.score >= state.target:
                state.match_status = "COMPLETED"
                state.result_summary = f"{state.batting_team} won by {state.wickets_remaining} wickets"
            elif state.balls_remaining == 0 or state.wickets == 10:
                state.match_status = "COMPLETED"
                if state.score == state.target - 1:
                    state.result_summary = "Match Tied"
                else:
                    margin = state.target - 1 - state.score
                    state.result_summary = f"{state.bowling_team} won by {margin} runs"

        elif state.balls_remaining == 0 or state.wickets == 10:
            # 1st Innings completed
            state.match_status = "INNINGS_COMPLETED"
            state.result_summary = f"{state.batting_team} set a target of {state.score + 1}"

        logger.info(
            f"Delivery [{delivery.delivery_id}]: Score={state.score}/{state.wickets} "
            f"({state.overs_formatted} ov), Striker={state.striker.name} {state.striker.runs}({state.striker.balls})"
        )

        return state
