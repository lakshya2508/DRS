"""
AI DRS & Autonomous Match Engine — Master End-to-End Live Demonstration Script
"""

import json
import time
from pathlib import Path

from ai_drs.api.review_service import ReviewPipelineService
from ai_drs.ingestion.video_ingestion import create_synthetic_video
from ai_drs.match.analytics_engine import MatchAnalyticsEngine
from ai_drs.match.condition_engine import MatchConditionEngine
from ai_drs.match.delivery_state_machine import DeliveryStateMachine
from ai_drs.match.match_state_engine import MatchStateEngine
from ai_drs.match.models import DeliveryEvent
from ai_drs.match.player_engines import BatsmanEngine, BowlerEngine
from ai_drs.match.toss_engine import TossEngine


def run_drs_demo():
    print("\n" + "=" * 70)
    print(" DEMO PART 1: SINGLE-CAMERA AI DRS LBW REVIEW PIPELINE")
    print("=" * 70)

    demo_video_path = Path("data/raw/demo_delivery.mp4")
    print(f"[1/3] Generating synthetic delivery video at '{demo_video_path}'...")
    create_synthetic_video(demo_video_path, num_frames=18, width=1280, height=720, fps=30.0)

    print("[2/3] Processing video through full E2E AI DRS Review Pipeline...")
    t0 = time.time()
    pipeline = ReviewPipelineService()
    result = pipeline.process_video(demo_video_path, batter_stance="RHB")
    elapsed = time.time() - t0

    print(f"\n[3/3] AI DRS REVIEW COMPLETE (Processing Time: {elapsed:.2f}s):")
    print("-" * 50)
    print(f" Review ID:        {result.review_id}")
    print(f" FINAL DECISION:   {result.result}")
    print(f" Confidence Score: {result.confidence:.1%}")
    print(f" Recommendation:   {result.recommendation_reason}")
    print("-" * 50)
    print(" COMPUTER VISION EVIDENCE BREAKDOWN:")
    print(f"  * Pitching Zone: {result.pitching['zone']} (Confidence: {result.pitching['confidence']:.2f})")
    print(f"  * Impact Zone:   {result.impact['zone']} (Confidence: {result.impact['confidence']:.2f})")
    print(f"  * Wicket Hit:    {result.wicket['hit_result']} (X={result.wicket['projected_x_m']:.3f}m, Z={result.wicket['projected_z_m']:.3f}m)")
    print(f"  * Track Length:  {result.ball_track['total_frames']} frames ({result.ball_track['coverage_ratio']:.1%} coverage)")
    print(f"  * Calibration:   Reprojection Error = {result.calibration['reprojection_error_px']:.2f}px")



def run_match_engine_demo():
    print("\n" + "=" * 70)
    print(" DEMO PART 2: L99 GOD MODE -- AUTONOMOUS MATCH ENGINE")
    print("=" * 70)

    # 1. Initialize Match & Toss
    print("[1/5] Initializing Match & Conducting Official Coin Toss...")
    match_engine = MatchStateEngine()
    toss = TossEngine.conduct_toss(
        team_a="Team India",
        team_b="Team Australia",
        caller_team="Team India",
        caller_call="HEADS",
        winner_decision="BAT"
    )

    state = match_engine.initialize_match(
        match_id="MATCH-IND-AUS-2026",
        team_a="Team India",
        team_b="Team Australia",
        striker_name="Virat Kohli",
        non_striker_name="Rohit Sharma",
        bowler_name="Mitchell Starc",
        total_overs=20,
        target=180,
        toss=toss
    )

    print(f"  * Toss Winner: {toss.toss_winner} (Chose to {toss.toss_choice})")
    print(f"  * Batting:     {state.batting_team}")
    print(f"  * Bowling:     {state.bowling_team}")
    print(f"  * Target:      Need {state.target} runs in {state.total_overs} overs (RRR: {state.required_run_rate:.2f})")

    # 2. Simulate Delivery Stream via 9-Stage FSM
    fsm = DeliveryStateMachine()
    condition_engine = MatchConditionEngine()
    analytics_engine = MatchAnalyticsEngine()

    match_history = [state.model_copy(deep=True)]

    deliveries_data = [
        # Over 1
        {"runs": 4, "is_w": False, "w_type": None, "new_b": None, "speed": 143.5},
        {"runs": 1, "is_w": False, "w_type": None, "new_b": None, "speed": 145.0},
        {"runs": 6, "is_w": False, "w_type": None, "new_b": None, "speed": 141.2},
        {"runs": 0, "is_w": False, "w_type": None, "new_b": None, "speed": 146.8},
        {"runs": 2, "is_w": False, "w_type": None, "new_b": None, "speed": 142.0},
        {"runs": 0, "is_w": True,  "w_type": "BOWLED", "new_b": "Suryakumar Yadav", "speed": 148.2},
        # Over 2
        {"runs": 4, "is_w": False, "w_type": None, "new_b": None, "speed": 138.5},
        {"runs": 1, "is_w": False, "w_type": None, "new_b": None, "speed": 139.0},
        {"runs": 4, "is_w": False, "w_type": None, "new_b": None, "speed": 140.5},
        {"runs": 6, "is_w": False, "w_type": None, "new_b": None, "speed": 142.1},
        {"runs": 1, "is_w": False, "w_type": None, "new_b": None, "speed": 139.8},
        {"runs": 4, "is_w": False, "w_type": None, "new_b": None, "speed": 141.0},
    ]

    print("\n[2/5] Processing 2 Overs through 9-Stage Delivery FSM...")
    print("-" * 70)

    for i, d in enumerate(deliveries_data, 1):
        deliv = DeliveryEvent(
            delivery_id=f"DELIV_{i}",
            over_number=(i - 1) // 6,
            ball_number_in_over=((i - 1) % 6) + 1,
            striker_name=state.striker.name,
            non_striker_name=state.non_striker.name,
            bowler_name="Mitchell Starc" if i <= 6 else "Pat Cummins",
            runs_off_bat=d["runs"],
            is_wicket=d["is_w"],
            wicket_type=d["w_type"],
            new_batsman_name=d["new_b"],
            ball_speed_kmh=d["speed"]
        )

        state, exec_log = fsm.process_delivery(deliv, state, is_validated=True)
        match_history.append(state.model_copy(deep=True))

        print(f" Ball {state.overs_formatted} | Code: {deliv.runs_off_bat if not deliv.is_wicket else 'W'} | "
              f"Score: {state.score}/{state.wickets} | Striker: {state.striker.name} ({state.striker.runs}) | "
              f"FSM: {exec_log.current_stage.value}")

    print("-" * 70)

    # 3. Cricbuzz Live Cards
    print("\n[3/5] CRICBUZZ-STYLE LIVE PLAYER CARDS:")
    striker_card = BatsmanEngine.get_cricbuzz_card(state.striker)
    non_striker_card = BatsmanEngine.get_cricbuzz_card(state.non_striker)
    bowler_card = BowlerEngine.get_cricbuzz_card(state.bowler)

    print(f"  [BATTER] STRIKER:     {striker_card.formatted_string}")
    print(f"  [BATTER] NON-STRIKER: {non_striker_card.formatted_string}")
    print(f"  [BOWLER] CURRENT:     {bowler_card.formatted_string}")

    # 4. Live Match Condition Panel
    print("\n[4/5] LIVE MATCH CONDITION PANEL:")
    cond = condition_engine.compute_conditions(state)
    print(f"  * Scoreboard:   {cond.current_score}/{cond.wickets_lost} ({cond.overs_formatted} Overs)")
    print(f"  * Target Chase: Need {cond.runs_required} runs from {cond.balls_remaining} balls")
    print(f"  * Run Rates:    CRR = {cond.current_run_rate:.2f} | RRR = {cond.required_run_rate:.2f}")
    print(f"  * Situation:    [{cond.situation_classification}] {cond.situation_description}")
    print(f"  * Baseline Proj:{cond.projected_score} runs")

    # 5. Match Intelligence Analytics
    print("\n[5/5] MATCH INTELLIGENCE ANALYTICS:")
    analytics = analytics_engine.generate_analytics(match_history)
    print(f"  * Run Rate Trend by Over: {[p.run_rate for p in analytics.run_rate_trend]}")
    print(f"  * Over Pressure Index:   {analytics.pressure_trend}")
    print(f"  * Wickets Timeline:     {[{'W': w.wicket_number, 'Score': w.score, 'Over': w.overs_formatted, 'Batter': w.player_name} for w in analytics.wicket_timeline]}")
    print(f"  * Score Projection Range: Min={analytics.score_projection.min_projected_score}, Expected={analytics.score_projection.expected_projected_score}, Max={analytics.score_projection.max_projected_score}")

    print("=" * 70)
    print(" LIVE DEMONSTRATION COMPLETE SUCCESS")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    run_drs_demo()
    run_match_engine_demo()
