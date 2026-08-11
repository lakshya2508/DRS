"""
Unit tests for Real-Time Win Probability & DLS Momentum Index Engine Module
"""

import pytest

from ai_drs.match.models import MatchState
from ai_drs.match.momentum_engine import MomentumEngine, WinProbabilityIndex


def test_win_probability_first_innings():
    match_state = MatchState(
        match_id="M_PROB_1",
        team_a="India",
        team_b="Australia",
        runs=120,
        wickets=2,
        overs=12,
        legal_balls=0,
        is_target_set=False
    )

    prob = MomentumEngine.calculate_win_probability(match_state)

    assert isinstance(prob, WinProbabilityIndex)
    assert prob.match_id == "M_PROB_1"
    assert prob.team_a_win_pct >= 50.0
    assert prob.team_a_win_pct + prob.team_b_win_pct == 100.0


def test_win_probability_chase_target_achieved():
    match_state = MatchState(
        match_id="M_PROB_2",
        team_a="India",
        team_b="Australia",
        runs=155,
        wickets=3,
        target_runs=150,
        is_target_set=True
    )

    prob = MomentumEngine.calculate_win_probability(match_state)

    assert prob.team_b_win_pct == 100.0
    assert prob.team_a_win_pct == 0.0
    assert prob.favored_team == "Australia"
