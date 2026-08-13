"""
Unit tests for Monte Carlo 10,000-Innings Match Simulator Module
"""

import pytest

from ai_drs.simulation.monte_carlo_simulator import (
    MonteCarloMatchSimulator,
    MonteCarloSimulationResult,
)


def test_monte_carlo_simulator():
    res = MonteCarloMatchSimulator.run_monte_carlo_simulation(num_simulations=500)

    assert isinstance(res, MonteCarloSimulationResult)
    assert res.simulations_count == 500
    assert 40.0 <= res.team_a_win_pct <= 60.0
    assert 40.0 <= res.team_b_win_pct <= 60.0
    assert res.mean_runs_scored > 140.0
