"""
FastAPI Router for Autonomous Cricket Match Engine (God Mode Endpoints)
"""

from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger
from ai_drs.match.analytics_engine import MatchAnalyticsEngine, MatchAnalyticsPayload
from ai_drs.match.condition_engine import MatchConditionEngine, MatchConditionPayload
from ai_drs.match.delivery_state_machine import DeliveryStateExecution, DeliveryStateMachine
from ai_drs.match.match_state_engine import MatchStateEngine
from ai_drs.match.models import DeliveryEvent, MatchState, TossState
from ai_drs.match.player_engines import (
    BatsmanCardPayload,
    BatsmanEngine,
    BowlerCardPayload,
    BowlerEngine,
)
from ai_drs.match.toss_engine import TossEngine

logger = setup_logger("ai_drs.api.match")

router = APIRouter(prefix="/api/v1/match", tags=["Match Engine"])

# In-memory match databases
matches_db: Dict[str, MatchState] = {}
match_history_db: Dict[str, List[MatchState]] = {}

fsm = DeliveryStateMachine()
condition_engine = MatchConditionEngine()
analytics_engine = MatchAnalyticsEngine()


class CreateMatchRequest(BaseModel):
    match_id: str
    team_a: str
    team_b: str
    striker_name: str
    non_striker_name: str
    bowler_name: str
    total_overs: int = Field(default=20, ge=1)
    target: Optional[int] = Field(default=None, ge=1)


class TossRequest(BaseModel):
    caller_team: str
    caller_call: str = Field(default="HEADS", description="'HEADS' or 'TAILS'")
    winner_decision: Optional[str] = Field(default=None, description="'BAT' or 'BOWL'")


class DeliveryResponse(BaseModel):
    match_state: MatchState
    fsm_execution: DeliveryStateExecution


class LiveCardsResponse(BaseModel):
    striker_card: BatsmanCardPayload
    non_striker_card: BatsmanCardPayload
    bowler_card: BowlerCardPayload


@router.post("/create", response_model=MatchState, status_code=status.HTTP_201_CREATED)
def create_match(payload: CreateMatchRequest):
    """Initializes a new match state."""
    state = MatchStateEngine.initialize_match(
        match_id=payload.match_id,
        team_a=payload.team_a,
        team_b=payload.team_b,
        striker_name=payload.striker_name,
        non_striker_name=payload.non_striker_name,
        bowler_name=payload.bowler_name,
        total_overs=payload.total_overs,
        target=payload.target
    )
    matches_db[payload.match_id] = state
    match_history_db[payload.match_id] = [state.model_copy(deep=True)]
    return state


@router.post("/{match_id}/toss", response_model=MatchState)
def conduct_toss(match_id: str, payload: TossRequest):
    """Executes official match coin toss and assigns batting/bowling teams."""
    if match_id not in matches_db:
        raise HTTPException(status_code=404, detail=f"Match '{match_id}' not found.")

    state = matches_db[match_id]
    try:
        toss_state = TossEngine.conduct_toss(
            team_a=state.team_a,
            team_b=state.team_b,
            caller_team=payload.caller_team,
            caller_call=payload.caller_call,
            winner_decision=payload.winner_decision
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    state.toss = toss_state
    state.batting_team = toss_state.batting_team
    state.bowling_team = toss_state.bowling_team
    matches_db[match_id] = state
    match_history_db[match_id].append(state.model_copy(deep=True))
    return state


@router.post("/{match_id}/delivery", response_model=DeliveryResponse)
def process_delivery(match_id: str, delivery: DeliveryEvent, is_validated: bool = Query(True)):
    """Processes a delivery through the 9-stage state machine and updates MatchState."""
    if match_id not in matches_db:
        raise HTTPException(status_code=404, detail=f"Match '{match_id}' not found.")

    state = matches_db[match_id]
    new_state, fsm_exec = fsm.process_delivery(delivery, state, is_validated=is_validated)

    matches_db[match_id] = new_state
    if is_validated:
        match_history_db[match_id].append(new_state.model_copy(deep=True))

    return DeliveryResponse(match_state=new_state, fsm_execution=fsm_exec)


@router.get("/{match_id}/scoreboard", response_model=MatchState)
def get_scoreboard(match_id: str):
    """Retrieves authoritative Cricbuzz live scoreboard MatchState."""
    if match_id not in matches_db:
        raise HTTPException(status_code=404, detail=f"Match '{match_id}' not found.")
    return matches_db[match_id]


@router.get("/{match_id}/cards", response_model=LiveCardsResponse)
def get_live_cards(match_id: str):
    """Retrieves Cricbuzz-style live striker, non-striker, and bowler cards."""
    if match_id not in matches_db:
        raise HTTPException(status_code=404, detail=f"Match '{match_id}' not found.")

    state = matches_db[match_id]
    striker_card = BatsmanEngine.get_cricbuzz_card(state.striker)
    non_striker_card = BatsmanEngine.get_cricbuzz_card(state.non_striker)
    bowler_card = BowlerEngine.get_cricbuzz_card(state.bowler)

    return LiveCardsResponse(
        striker_card=striker_card,
        non_striker_card=non_striker_card,
        bowler_card=bowler_card
    )


@router.get("/{match_id}/condition-panel", response_model=MatchConditionPayload)
def get_condition_panel(match_id: str):
    """Retrieves live match condition panel and situation classification."""
    if match_id not in matches_db:
        raise HTTPException(status_code=404, detail=f"Match '{match_id}' not found.")

    state = matches_db[match_id]
    return condition_engine.compute_conditions(state)


@router.get("/{match_id}/analytics", response_model=MatchAnalyticsPayload)
def get_match_analytics(match_id: str):
    """Retrieves match intelligence analytics (run rate trends, wickets timeline, pressure index, score projection)."""
    if match_id not in matches_db:
        raise HTTPException(status_code=404, detail=f"Match '{match_id}' not found.")

    history = match_history_db.get(match_id, [])
    payload = analytics_engine.generate_analytics(history)
    if payload is None:
        raise HTTPException(status_code=400, detail="Insufficient match history for analytics.")
    return payload
