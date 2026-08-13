"""
Unit tests for Synthetic Edge-Case Scenario Generator Module
"""

import pytest

from ai_drs.simulation.synthetic_scenario_generator import (
    SyntheticDRSScenario,
    SyntheticScenarioGenerator,
)


def test_synthetic_scenario_generator():
    scenarios = SyntheticScenarioGenerator.generate_drs_edge_cases()

    assert len(scenarios) == 3
    assert all(isinstance(s, SyntheticDRSScenario) for s in scenarios)
    assert any(s.scenario_id == "SCEN_UMPIRES_CALL_WICKETS" for s in scenarios)
    assert any(s.scenario_id == "SCEN_PITCHING_OUTSIDE_LEG" for s in scenarios)
