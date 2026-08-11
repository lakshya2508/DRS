"""
Unit tests for MatchConditionEngine Module
"""

import pytest

from ai_drs.match.condition_engine import MatchConditionEngine, MatchConditionPayload
from ai_drs.match.match_state_engine import MatchStateEngine


@pytest.fixture
def chase_match_state():
    engine = MatchStateEngine()
    return engine.initialize_match(
        match_id="M301",
        team_a="India",
        team_b="Australia",
        striker_name="V. Kohli",
        non_striker_name="R. Sharma",
        bowler_name="M. Starc",
        total_overs=20,
        target=180
    )


def test_chase_comfortable_situation(chase_match_state):
    engine = MatchStateEngine()
    state = chase_match_state

    # Set score to 120/2 in 15 overs (Need 60 from 30 balls, RRR = 12.0)
    state.score = 150
    state.total_legal_balls = 90  # 15 overs
    state.balls_remaining = 30    # 5 overs
    state.wickets = 2
    state.wickets_remaining = 8
    state.runs_required = 30
    state.required_run_rate = 6.0  # Need 30 off 5 overs = RRR 6.0

    cond_engine = MatchConditionEngine()
    cond = cond_engine.compute_conditions(state)

    assert isinstance(cond, MatchConditionPayload)
    assert cond.situation_classification == "COMFORTABLE"
    assert "COMFORTABLE" in cond.situation_description
    assert cond.runs_required == 30
    assert cond.balls_remaining == 30


def test_chase_critical_situation(chase_match_state):
    state = chase_match_state
    state.score = 150
    state.total_legal_balls = 114  # 19 overs
    state.balls_remaining = 6      # 1 over
    state.wickets = 9
    state.wickets_remaining = 1
    state.runs_required = 30       # Need 30 off 6 balls (RRR 30.0)
    state.required_run_rate = 30.0

    cond_engine = MatchConditionEngine()
    cond = cond_engine.compute_conditions(state)

    assert cond.situation_classification == "CRITICAL"
    assert "CRITICAL" in cond.situation_description


def test_first_innings_conditions():
    engine = MatchStateEngine()
    state = engine.initialize_match(
        match_id="M302",
        team_a="India",
        team_b="Australia",
        striker_name="V. Kohli",
        non_striker_name="R. Sharma",
        bowler_name="M. Starc",
        total_overs=20,
        target=None
    )

    state.score = 80
    state.total_legal_balls = 60
    state.balls_remaining = 60
    state.current_run_rate = 8.0

    cond_engine = MatchConditionEngine()
    cond = cond_engine.compute_conditions(state)

    assert cond.target is None
    assert cond.situation_classification == "COMFORTABLE"
    assert cond.projected_score == 160  # 80 + 8.0 * 10 overs
