"""
Unit tests for Tournament Leaderboards & Player Honors Module
"""

import pytest

from ai_drs.tournament.leaderboards import (
    LeaderboardEngine,
    PlayerLeaderboardStats,
    TournamentLeaderboardPackage,
)


def test_leaderboard_engine_orange_and_purple_cap():
    engine = LeaderboardEngine("T_LEADER_1")

    engine.update_player_batting("V. Kohli", "India", runs=85, balls=50, fours=8, sixes=3)
    engine.update_player_batting("R. Sharma", "India", runs=60, balls=30, fours=5, sixes=4)

    engine.update_player_bowling("J. Bumrah", "India", wickets=4, overs=4.0, runs_conceded=18)
    engine.update_player_bowling("M. Shami", "India", wickets=2, overs=4.0, runs_conceded=25)

    package = engine.get_leaderboards()

    assert isinstance(package, TournamentLeaderboardPackage)
    assert package.orange_cap_holder is not None
    assert package.orange_cap_holder.player_name == "V. Kohli"
    assert package.orange_cap_holder.runs == 85
    assert package.orange_cap_holder.strike_rate == 170.0

    assert package.purple_cap_holder is not None
    assert package.purple_cap_holder.player_name == "J. Bumrah"
    assert package.purple_cap_holder.wickets == 4
    assert package.purple_cap_holder.bowling_economy == 4.5
