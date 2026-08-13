"""
Tournament REST API Router for Standings, Points Tables & Leaderboards
"""

from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel

from ai_drs.common.logging import setup_logger
from ai_drs.tournament.leaderboards import LeaderboardEngine, TournamentLeaderboardPackage
from ai_drs.tournament.tournament_engine import TournamentEngine, TournamentStandings

logger = setup_logger("ai_drs.api.tournament")

tournament_router = APIRouter(prefix="/api/v1/tournament", tags=["Tournament Engine"])
router = tournament_router


# In-memory tournament engines
tournaments_db: Dict[str, TournamentEngine] = {}
leaderboards_db: Dict[str, LeaderboardEngine] = {}


class CreateTournamentRequest(BaseModel):
    tournament_id: str
    tournament_name: str
    teams: List[str]


class MatchResultRequest(BaseModel):
    team_a: str
    team_b: str
    runs_a: int
    overs_a: float
    wickets_a: int
    runs_b: int
    overs_b: float
    wickets_b: int
    winner_team: Optional[str] = None


@tournament_router.post("/create", response_model=TournamentStandings, status_code=status.HTTP_201_CREATED)
def create_tournament(req: CreateTournamentRequest):
    """Initializes a new tournament with participating teams."""
    engine = TournamentEngine(req.tournament_id, req.tournament_name)
    leaderboard = LeaderboardEngine(req.tournament_id)

    for team in req.teams:
        engine.register_team(team)

    tournaments_db[req.tournament_id] = engine
    leaderboards_db[req.tournament_id] = leaderboard

    logger.info(f"Created Tournament [{req.tournament_id}] with {len(req.teams)} teams.")
    return engine.get_standings()


@tournament_router.post("/{tournament_id}/match-result", response_model=TournamentStandings)
def record_tournament_match(tournament_id: str, req: MatchResultRequest):
    """Records match result and updates tournament points table and NRR."""
    if tournament_id not in tournaments_db:
        raise HTTPException(status_code=404, detail=f"Tournament '{tournament_id}' not found.")

    engine = tournaments_db[tournament_id]
    engine.record_match_result(
        team_a=req.team_a,
        team_b=req.team_b,
        runs_a=req.runs_a,
        overs_a=req.overs_a,
        wickets_a=req.wickets_a,
        runs_b=req.runs_b,
        overs_b=req.overs_b,
        wickets_b=req.wickets_b,
        winner_team=req.winner_team
    )
    return engine.get_standings()


@tournament_router.get("/{tournament_id}/standings", response_model=TournamentStandings)
def get_tournament_standings(tournament_id: str):
    """Retrieves current tournament points table standings."""
    if tournament_id not in tournaments_db:
        raise HTTPException(status_code=404, detail=f"Tournament '{tournament_id}' not found.")
    return tournaments_db[tournament_id].get_standings()


@tournament_router.get("/{tournament_id}/leaderboards", response_model=TournamentLeaderboardPackage)
def get_tournament_leaderboards(tournament_id: str):
    """Retrieves Orange Cap, Purple Cap, and player tournament rankings."""
    if tournament_id not in leaderboards_db:
        raise HTTPException(status_code=404, detail=f"Tournament '{tournament_id}' not found.")
    return leaderboards_db[tournament_id].get_leaderboards()
