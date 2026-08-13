"""
Unit tests for DLS 4.0 Revised Target Score Recalculator Module
"""

import math
import pytest

from ai_drs.match.dls_target_calculator import DLSTargetCalculator, DLSTargetResult


def test_dls_target_calculator_equal_resources():
    res = DLSTargetCalculator.calculate_revised_target(
        team_a_runs=180, team_a_resources_pct=100.0, team_b_resources_pct=100.0
    )
    assert isinstance(res, DLSTargetResult)
    assert res.revised_target_runs == 181


def test_dls_target_calculator_reduced_resources():
    # Team A scored 180 (100% resources). Team B gets 80% resources (16 overs).
    res = DLSTargetCalculator.calculate_revised_target(
        team_a_runs=180, team_a_resources_pct=100.0, team_b_resources_pct=80.0
    )
    assert res.revised_target_runs == 145  # 180 * 0.80 = 144 + 1
