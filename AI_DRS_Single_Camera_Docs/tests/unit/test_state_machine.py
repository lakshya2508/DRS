"""
Unit tests for Delivery State Machine Module
"""

import pytest

from ai_drs.match.delivery_state_machine import DeliveryStage, DeliveryStateMachine
from ai_drs.match.match_state_engine import MatchStateEngine
from ai_drs.match.models import DeliveryEvent


@pytest.fixture
def initial_match():
    engine = MatchStateEngine()
    return engine.initialize_match(
        match_id="M201",
        team_a="India",
        team_b="England",
        striker_name="V. Kohli",
        non_striker_name="R. Sharma",
        bowler_name="J. Anderson"
    )


def test_delivery_state_machine_happy_path(initial_match):
    fsm = DeliveryStateMachine()
    deliv = DeliveryEvent(
        delivery_id="D1.1",
        over_number=0,
        ball_number_in_over=1,
        striker_name="V. Kohli",
        non_striker_name="R. Sharma",
        bowler_name="J. Anderson",
        runs_off_bat=4
    )

    new_state, exec_log = fsm.process_delivery(deliv, initial_match, is_validated=True)

    assert exec_log.current_stage == DeliveryStage.DELIVERY_COMPLETE
    assert exec_log.error_message is None
    assert len(exec_log.history) == 9
    assert exec_log.history[0] == DeliveryStage.DELIVERY_START
    assert exec_log.history[-1] == DeliveryStage.DELIVERY_COMPLETE
    assert new_state.score == 4


def test_unvalidated_delivery_event_rejection(initial_match):
    fsm = DeliveryStateMachine()
    deliv = DeliveryEvent(
        delivery_id="D1.1",
        over_number=0,
        ball_number_in_over=1,
        striker_name="V. Kohli",
        non_striker_name="R. Sharma",
        bowler_name="J. Anderson",
        runs_off_bat=6
    )

    # Pass unvalidated delivery (is_validated = False)
    new_state, exec_log = fsm.process_delivery(deliv, initial_match, is_validated=False)

    assert exec_log.current_stage == DeliveryStage.FAILED
    assert "validation failed" in exec_log.error_message.lower()
    # MatchState score remains 0 (no mutation occurred)
    assert new_state.score == 0
    assert initial_match.score == 0
