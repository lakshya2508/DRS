"""
Unit tests for ProjectionEngine and MatchAnalyticsEngine
"""

import pytest

from ai_drs.match.analytics_engine import (
    MatchAnalyticsEngine,
    ProjectionEngine,
    MatchAnalyticsPayload,
    ProjectionRange,
)
from ai_drs.match.match_state_engine import MatchStateEngine
from ai_drs.match.models import DeliveryEvent


@pytest.fixture
def match_history():
    engine = MatchStateEngine()
    state = engine.initialize_match(
        match_id="M401",
        team_a="India",
        team_b="Australia",
        striker_name="V. Kohli",
        non_striker_name="R. Sharma",
        bowler_name="M. Starc",
        total_overs=20,
        target=180
    )

    history = [state]

    # Simulate 12 deliveries (2 overs)
    for i in range(12):
        is_w = (i == 5)  # Wicket on 6th ball
        deliv = DeliveryEvent(
            delivery_id=f"D{i+1}",
            over_number=i // 6,
            ball_number_in_over=(i % 6) + 1,
            striker_name=state.striker.name,
            non_striker_name=state.non_striker.name,
            bowler_name="M. Starc",
            runs_off_bat=4 if i % 2 == 0 else 1,
            is_wicket=is_w,
            wicket_type="BOWLED" if is_w else None,
            new_batsman_name="S. Yadav" if is_w else None
        )
        state = engine.apply_delivery(state, deliv)
        history.append(state.model_copy(deep=True))

    return history


def test_projection_engine(match_history):
    latest_state = match_history[-1]
    proj = ProjectionEngine.compute_projection(latest_state)

    assert isinstance(proj, ProjectionRange)
    assert proj.min_projected_score <= proj.expected_projected_score
    assert proj.expected_projected_score <= proj.max_projected_score
    assert proj.expected_projected_score <= 180  # Target capped


def test_match_analytics_engine(match_history):
    analytics_engine = MatchAnalyticsEngine()
    analytics = analytics_engine.generate_analytics(match_history)

    assert isinstance(analytics, MatchAnalyticsPayload)
    assert analytics.match_id == "M401"
    assert len(analytics.run_rate_trend) == 2  # 2 overs completed
    assert len(analytics.wicket_timeline) == 1  # 1 wicket fell
    assert analytics.wicket_timeline[0].wicket_number == 1
    assert len(analytics.pressure_trend) == 2


def test_empty_analytics():
    analytics_engine = MatchAnalyticsEngine()
    assert analytics_engine.generate_analytics([]) is None
