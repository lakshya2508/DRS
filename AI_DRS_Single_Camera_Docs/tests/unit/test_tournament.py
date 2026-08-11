"""
Unit tests for Tournament Operations & Net Run Rate Engine Module
"""

import pytest

from ai_drs.tournament.tournament_engine import (
    TeamPointsEntry,
    TournamentEngine,
    TournamentStandings,
)


def test_tournament_engine_points_and_nrr():
    engine = TournamentEngine("T_IPL_2026", "IPL T20 League")

    # Match 1: India (180/4 in 20.0) vs Australia (160/8 in 20.0) -> India wins
    engine.record_match_result(
        team_a="India",
        team_b="Australia",
        runs_a=180,
        overs_a=20.0,
        wickets_a=4,
        runs_b=160,
        overs_b=20.0,
        wickets_b=8,
        winner_team="India"
    )

    standings = engine.get_standings()

    assert isinstance(standings, TournamentStandings)
    assert standings.standings[0].team_name == "India"
    assert standings.standings[0].points == 2
    assert standings.standings[0].nrr == +1.0  # (180/20) - (160/20) = 9.0 - 8.0 = +1.0

    assert standings.standings[1].team_name == "Australia"
    assert standings.standings[1].points == 0
    assert standings.standings[1].nrr == -1.0


def test_overs_decimal_conversion():
    assert TournamentEngine._overs_to_decimal_balls(19.3) == 19.5
    assert TournamentEngine._overs_to_decimal_balls(10.0) == 10.0
