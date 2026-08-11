"""
Delivery State Machine for AI DRS (9-Stage Lifecycle & Validation Guarding)
"""

from enum import Enum
from typing import List, Optional, Tuple
from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger
from ai_drs.match.match_state_engine import MatchStateEngine
from ai_drs.match.models import DeliveryEvent, MatchState

logger = setup_logger("ai_drs.match.fsm")


class DeliveryStage(str, Enum):
    """The 9 mandatory stages of a delivery lifecycle."""
    DELIVERY_START = "DELIVERY_START"
    BALL_TRACKING = "BALL_TRACKING"
    EVENT_RECOGNITION = "EVENT_RECOGNITION"
    EVENT_VALIDATION = "EVENT_VALIDATION"
    MATCH_STATE_UPDATE = "MATCH_STATE_UPDATE"
    PLAYER_STAT_UPDATE = "PLAYER_STAT_UPDATE"
    CONDITION_UPDATE = "CONDITION_UPDATE"
    SCOREBOARD_UPDATE = "SCOREBOARD_UPDATE"
    DELIVERY_COMPLETE = "DELIVERY_COMPLETE"
    FAILED = "FAILED"


VALID_TRANSITIONS = {
    DeliveryStage.DELIVERY_START: [DeliveryStage.BALL_TRACKING, DeliveryStage.FAILED],
    DeliveryStage.BALL_TRACKING: [DeliveryStage.EVENT_RECOGNITION, DeliveryStage.FAILED],
    DeliveryStage.EVENT_RECOGNITION: [DeliveryStage.EVENT_VALIDATION, DeliveryStage.FAILED],
    DeliveryStage.EVENT_VALIDATION: [DeliveryStage.MATCH_STATE_UPDATE, DeliveryStage.FAILED],
    DeliveryStage.MATCH_STATE_UPDATE: [DeliveryStage.PLAYER_STAT_UPDATE, DeliveryStage.FAILED],
    DeliveryStage.PLAYER_STAT_UPDATE: [DeliveryStage.CONDITION_UPDATE, DeliveryStage.FAILED],
    DeliveryStage.CONDITION_UPDATE: [DeliveryStage.SCOREBOARD_UPDATE, DeliveryStage.FAILED],
    DeliveryStage.SCOREBOARD_UPDATE: [DeliveryStage.DELIVERY_COMPLETE, DeliveryStage.FAILED],
    DeliveryStage.DELIVERY_COMPLETE: [],
    DeliveryStage.FAILED: []
}


class DeliveryStateExecution(BaseModel):
    """Execution log payload for a delivery state machine run."""
    delivery_id: str
    current_stage: DeliveryStage
    history: List[DeliveryStage] = Field(default_factory=list)
    is_validated: bool = Field(default=False)
    error_message: Optional[str] = Field(default=None)


class DeliveryStateMachine:
    """Manages the 9-stage delivery state machine and guards MatchState mutations."""

    def __init__(self):
        self.state_engine = MatchStateEngine()

    def process_delivery(
        self,
        delivery_event: DeliveryEvent,
        match_state: MatchState,
        is_validated: bool = True
    ) -> Tuple[MatchState, DeliveryStateExecution]:
        """Runs the 9-stage delivery lifecycle and updates MatchState if validated."""
        execution = DeliveryStateExecution(
            delivery_id=delivery_event.delivery_id,
            current_stage=DeliveryStage.DELIVERY_START,
            history=[DeliveryStage.DELIVERY_START],
            is_validated=is_validated
        )

        stages_sequence = [
            DeliveryStage.BALL_TRACKING,
            DeliveryStage.EVENT_RECOGNITION,
            DeliveryStage.EVENT_VALIDATION,
            DeliveryStage.MATCH_STATE_UPDATE,
            DeliveryStage.PLAYER_STAT_UPDATE,
            DeliveryStage.CONDITION_UPDATE,
            DeliveryStage.SCOREBOARD_UPDATE,
            DeliveryStage.DELIVERY_COMPLETE
        ]

        updated_state = match_state

        for next_stage in stages_sequence:
            # Check validation guard before entering MATCH_STATE_UPDATE
            if next_stage == DeliveryStage.MATCH_STATE_UPDATE and not execution.is_validated:
                logger.error(
                    f"Delivery [{delivery_event.delivery_id}] failed validation guard. "
                    "Cannot mutate MatchState with unvalidated delivery events."
                )
                execution.current_stage = DeliveryStage.FAILED
                execution.history.append(DeliveryStage.FAILED)
                execution.error_message = "Event validation failed: unvalidated CV prediction"
                return match_state, execution

            # Validate state transition
            allowed = VALID_TRANSITIONS.get(execution.current_stage, [])
            if next_stage not in allowed:
                logger.error(f"Invalid FSM transition: {execution.current_stage} -> {next_stage}")
                execution.current_stage = DeliveryStage.FAILED
                execution.history.append(DeliveryStage.FAILED)
                execution.error_message = f"Invalid state transition: {execution.current_stage} -> {next_stage}"
                return match_state, execution

            # Advance stage
            execution.current_stage = next_stage
            execution.history.append(next_stage)

            # Perform stage actions
            if next_stage == DeliveryStage.MATCH_STATE_UPDATE:
                updated_state = self.state_engine.apply_delivery(match_state, delivery_event)

        logger.info(f"Delivery [{delivery_event.delivery_id}] completed 9-stage lifecycle successfully.")
        return updated_state, execution
