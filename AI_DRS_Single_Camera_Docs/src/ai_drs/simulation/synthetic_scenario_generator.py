"""
Synthetic Edge-Case Scenario Generator for DRS Pipeline Stress Testing
"""

from typing import List
from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.simulation.scenarios")


class SyntheticDRSScenario(BaseModel):
    """Schema representing synthetic DRS edge-case delivery scenario."""
    scenario_id: str
    scenario_name: str
    pitching_x_m: float
    impact_x_m: float
    wicket_hit_x_m: float
    expected_decision: str
    is_edge_case: bool = True


class SyntheticScenarioGenerator:
    """Generates synthetic edge-case delivery scenarios (Umpires Call, Clipping Stumps, Extreme Swing) for pipeline testing."""

    @staticmethod
    def generate_drs_edge_cases() -> List[SyntheticDRSScenario]:
        """Generates standard benchmark suite of synthetic DRS edge cases."""
        scenarios = [
            SyntheticDRSScenario(
                scenario_id="SCEN_UMPIRES_CALL_WICKETS",
                scenario_name="Clipping Outer Edge of Off Stump (Umpires Call Wickets)",
                pitching_x_m=0.0,
                impact_x_m=0.0,
                wicket_hit_x_m=0.11,  # Outer edge of stump (0.114m boundary)
                expected_decision="UMPIRES_CALL",
                is_edge_case=True
            ),
            SyntheticDRSScenario(
                scenario_id="SCEN_PITCHING_OUTSIDE_LEG",
                scenario_name="Pitching 1mm Outside Leg Stump Line",
                pitching_x_m=0.12,
                impact_x_m=0.0,
                wicket_hit_x_m=0.0,
                expected_decision="NOT_OUT",
                is_edge_case=True
            ),
            SyntheticDRSScenario(
                scenario_id="SCEN_EXTREME_INSWING_LBW",
                scenario_name="Extreme Inswing Pitching Outside Off, Impact In Line, Hitting Middle",
                pitching_x_m=-0.50,
                impact_x_m=0.0,
                wicket_hit_x_m=0.0,
                expected_decision="OUT",
                is_edge_case=True
            ),
        ]

        logger.info(f"Generated {len(scenarios)} Synthetic DRS Edge-Case Scenarios.")
        return scenarios
