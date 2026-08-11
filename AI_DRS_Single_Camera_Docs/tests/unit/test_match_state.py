"""
Unit tests for MatchState Engine and Match Data Models
"""

import pytest

from ai_drs.match.match_state_engine import MatchStateEngine
from ai_drs.match.models import DeliveryEvent, MatchState, TossState


@pytest.fixture
def initial_match_state():
    engine = MatchStateEngine()
    toss = TossState(
        toss_winner="Team India",
        toss_choice="BAT",
        batting_team="Team India",
        bowling_team="Team Australia"
    )
    return engine.initialize_match(
        match_id="M101",
        team_a="Team India",
        team_b="Team Australia",
        striker_name="V. Kohli",
        non_striker_name="R. Sharma",
        bowler_name="M. Starc",
        total_overs=20,
        target=180,
        toss=toss
    )


def test_match_initialization(initial_match_state):
    state = initial_match_state
    assert state.match_id == "M101"
    assert state.score == 0
    assert state.wickets == 0
    assert state.total_legal_balls == 0
    assert state.striker.name == "V. Kohli"
    assert state.non_striker.name == "R. Sharma"
    assert state.bowler.name == "M. Starc"
    assert state.target == 180
    assert state.runs_required == 180
    assert state.balls_remaining == 120
    assert state.required_run_rate == 9.0


def test_single_delivery_four(initial_match_state):
    engine = MatchStateEngine()
    deliv = DeliveryEvent(
        delivery_id="D1.1",
        over_number=0,
        ball_number_in_over=1,
        striker_name="V. Kohli",
        non_striker_name="R. Sharma",
        bowler_name="M. Starc",
        runs_off_bat=4,
        ball_speed_kmh=142.5
    )

    state = engine.apply_delivery(initial_match_state, deliv)

    assert state.score == 4
    assert state.total_legal_balls == 1
    assert state.overs_formatted == 0.1
    assert state.striker.runs == 4
    assert state.striker.balls == 1
    assert state.striker.fours == 1
    assert state.striker.strike_rate == 400.0
    assert state.bowler.runs_conceded == 4
    assert state.bowler.legal_balls == 1
    assert state.bowler.maximum_speed_kmh == 142.5
    # Even runs off bat: striker remains V. Kohli
    assert state.striker.name == "V. Kohli"


def test_strike_rotation_odd_runs(initial_match_state):
    engine = MatchStateEngine()
    deliv = DeliveryEvent(
        delivery_id="D1.1",
        over_number=0,
        ball_number_in_over=1,
        striker_name="V. Kohli",
        non_striker_name="R. Sharma",
        bowler_name="M. Starc",
        runs_off_bat=1
    )

    state = engine.apply_delivery(initial_match_state, deliv)

    assert state.score == 1
    # Odd run: striker rotated to R. Sharma
    assert state.striker.name == "R. Sharma"
    assert state.non_striker.name == "V. Kohli"


test_wide_delivery_extra = None  # Placeholder


def test_wide_delivery(initial_match_state):
    engine = MatchStateEngine()
    deliv = DeliveryEvent(
        delivery_id="D1.1",
        over_number=0,
        ball_number_in_over=1,
        striker_name="V. Kohli",
        non_striker_name="R. Sharma",
        bowler_name="M. Starc",
        wide_runs=1
    )

    state = engine.apply_delivery(initial_match_state, deliv)

    assert state.score == 1
    assert state.total_legal_balls == 0  # Wide does not count as legal ball
    assert state.striker.balls == 0      # Batter ball count unchanged
    assert state.bowler.runs_conceded == 1


def test_over_completion_strike_rotation(initial_match_state):
    engine = MatchStateEngine()
    state = initial_match_state

    # 6 dot balls in over
    for i in range(1, 7):
        deliv = DeliveryEvent(
            delivery_id=f"D1.{i}",
            over_number=0,
            ball_number_in_over=i,
            striker_name=state.striker.name,
            non_striker_name=state.non_striker.name,
            bowler_name="M. Starc",
            runs_off_bat=0
        )
        state = engine.apply_delivery(state, deliv)

    assert state.total_legal_balls == 6
    assert state.overs_formatted == 1.0
    # End of over: strike rotated to R. Sharma
    assert state.striker.name == "R. Sharma"
    assert state.non_striker.name == "V. Kohli"


def test_wicket_fall_and_batsman_replacement(initial_match_state):
    engine = MatchStateEngine()
    deliv = DeliveryEvent(
        delivery_id="D1.1",
        over_number=0,
        ball_number_in_over=1,
        striker_name="V. Kohli",
        non_striker_name="R. Sharma",
        bowler_name="M. Starc",
        is_wicket=True,
        wicket_type="LBW",
        new_batsman_name="S. Yadav"
    )

    state = engine.apply_delivery(initial_match_state, deliv)

    assert state.wickets == 1
    assert state.wickets_remaining == 9
    assert state.bowler.wickets == 1
    assert state.striker.name == "S. Yadav"
    assert state.non_striker.name == "R. Sharma"


def test_target_chase_completed(initial_match_state):
    engine = MatchStateEngine()
    state = initial_match_state

    # Hit 6 runs 30 times (180 runs)
    for i in range(30):
        deliv = DeliveryEvent(
            delivery_id=f"D{i}",
            over_number=i // 6,
            ball_number_in_over=(i % 6) + 1,
            striker_name=state.striker.name,
            non_striker_name=state.non_striker.name,
            bowler_name="M. Starc",
            runs_off_bat=6
        )
        state = engine.apply_delivery(state, deliv)

    assert state.score == 180
    assert state.match_status == "COMPLETED"
    assert "won by 10 wickets" in state.result_summary
