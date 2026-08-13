"""
Unit tests for Live DLS Par Score Ticker Engine Module
"""

import pytest

from ai_drs.match.dls_par_ticker import DLSParScoreTickerEngine, DLSParScoreTickerState


def test_dls_par_score_ticker():
    # Team A scored 180. Team B is 85/2 after 10.0 overs
    ticker = DLSParScoreTickerEngine.calculate_par_score_ticker(
        team_a_runs=180, overs_bowled=10.0, current_wickets=2, current_runs=85, total_overs=20.0
    )

    assert isinstance(ticker, DLSParScoreTickerState)
    assert ticker.par_score_runs > 0
    assert ticker.winning_team_if_stoppage in ("TEAM_A", "TEAM_B")
