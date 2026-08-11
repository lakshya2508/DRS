"""
Unit tests for TossEngine Module
"""

import pytest

from ai_drs.match.models import TossState
from ai_drs.match.toss_engine import TossEngine


def test_toss_caller_chooses_bat():
    toss = TossEngine.conduct_toss(
        team_a="India",
        team_b="Australia",
        caller_team="India",
        caller_call="HEADS",
        winner_decision="BAT"
    )

    assert isinstance(toss, TossState)
    assert toss.toss_choice == "BAT"
    if toss.toss_winner == "India":
        assert toss.batting_team == "India"
        assert toss.bowling_team == "Australia"
    else:
        assert toss.toss_winner == "Australia"
        assert toss.batting_team == "Australia"
        assert toss.bowling_team == "India"


def test_toss_caller_chooses_bowl():
    toss = TossEngine.conduct_toss(
        team_a="India",
        team_b="Australia",
        caller_team="India",
        caller_call="TAILS",
        winner_decision="BOWL"
    )

    assert toss.toss_choice == "BOWL"
    if toss.toss_winner == "India":
        assert toss.batting_team == "Australia"
        assert toss.bowling_team == "India"
    else:
        assert toss.batting_team == "India"
        assert toss.bowling_team == "Australia"


def test_toss_invalid_inputs():
    with pytest.raises(ValueError, match="Caller team"):
        TossEngine.conduct_toss("India", "Australia", caller_team="England")

    with pytest.raises(ValueError, match="Invalid coin call"):
        TossEngine.conduct_toss("India", "Australia", caller_team="India", caller_call="EDGE")

    with pytest.raises(ValueError, match="Invalid decision"):
        TossEngine.conduct_toss("India", "Australia", caller_team="India", winner_decision="FIELD_FIRST")


def test_toss_fairness_distribution():
    winners = []
    for _ in range(1000):
        t = TossEngine.conduct_toss("India", "Australia", caller_team="India", caller_call="HEADS", winner_decision="BAT")
        winners.append(t.toss_winner)

    india_wins = winners.count("India")
    aus_wins = winners.count("Australia")

    # Expect roughly 50% split (400 to 600 out of 1000)
    assert 380 <= india_wins <= 620
    assert 380 <= aus_wins <= 620
