"""
Monte Carlo 10,000-Innings Match Simulator Module
"""

import random
import numpy as np
from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.simulation.monte_carlo")


class MonteCarloSimulationResult(BaseModel):
    """Schema representing Monte Carlo stochastic match simulation results."""
    simulations_count: int
    team_a_win_pct: float = Field(ge=0.0, le=100.0)
    team_b_win_pct: float = Field(ge=0.0, le=100.0)
    tie_pct: float = Field(ge=0.0, le=100.0)
    mean_runs_scored: float = Field(ge=0.0)
    std_dev_runs: float = Field(ge=0.0)


class MonteCarloMatchSimulator:
    """Runs N stochastic Monte Carlo match simulations to calculate win probability distributions."""

    @staticmethod
    def run_monte_carlo_simulation(
        num_simulations: int = 1000,
        team_a_strength: float = 1.0,
        team_b_strength: float = 1.0,
        total_overs: float = 20.0
    ) -> MonteCarloSimulationResult:
        """Simulates stochastic match outcomes across num_simulations iterations."""
        np.random.seed(42)

        # Baseline T20 score distribution: Mean=160, Std=25
        a_scores = np.random.normal(160.0 * team_a_strength, 25.0, num_simulations)
        b_scores = np.random.normal(160.0 * team_b_strength, 25.0, num_simulations)

        a_wins = int(np.sum(a_scores > b_scores))
        b_wins = int(np.sum(b_scores > a_scores))
        ties = int(np.sum(np.abs(a_scores - b_scores) < 1.0))

        a_pct = float(a_wins / num_simulations * 100.0)
        b_pct = float(b_wins / num_simulations * 100.0)
        tie_pct = float(ties / num_simulations * 100.0)

        mean_runs = float(np.mean(a_scores))
        std_runs = float(np.std(a_scores))

        logger.info(
            f"Monte Carlo Simulation [{num_simulations} matches]: Team A Win={a_pct:.1f}%, "
            f"Team B Win={b_pct:.1f}%, Mean Runs={mean_runs:.1f} +/- {std_runs:.1f}"
        )

        return MonteCarloSimulationResult(
            simulations_count=num_simulations,
            team_a_win_pct=round(a_pct, 1),
            team_b_win_pct=round(b_pct, 1),
            tie_pct=round(tie_pct, 1),
            mean_runs_scored=round(mean_runs, 1),
            std_dev_runs=round(std_runs, 1)
        )
