"""
Tournament Operations & Net Run Rate (NRR) Engine for Autonomous Match Engine
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.tournament.engine")


class TeamPointsEntry(BaseModel):
    """Schema representing team standings in tournament points table."""
    team_name: str
    played: int = 0
    won: int = 0
    lost: int = 0
    tied: int = 0
    no_result: int = 0
    points: int = 0
    nrr: float = 0.0
    runs_scored: int = 0
    overs_faced: float = 0.0
    runs_conceded: int = 0
    overs_bowled: float = 0.0


class TournamentStandings(BaseModel):
    """Schema representing full tournament points table standings."""
    tournament_id: str
    tournament_name: str
    standings: List[TeamPointsEntry] = Field(default_factory=list)


class TournamentEngine:
    """Manages multi-match tournament operations, points calculation, and Net Run Rate (NRR)."""

    def __init__(self, tournament_id: str, tournament_name: str):
        self.tournament_id = tournament_id
        self.tournament_name = tournament_name
        self.teams: Dict[str, TeamPointsEntry] = {}

    def register_team(self, team_name: str):
        """Registers a team in the tournament."""
        if team_name not in self.teams:
            self.teams[team_name] = TeamPointsEntry(team_name=team_name)
            logger.info(f"Registered Team [{team_name}] in Tournament [{self.tournament_id}]")

    @staticmethod
    def _overs_to_decimal_balls(overs_float: float) -> float:
        """Converts cricket overs representation (e.g. 19.3) to exact overs decimal (19 + 3/6 = 19.5)."""
        full_overs = int(overs_float)
        balls = round((overs_float - full_overs) * 10)
        return float(full_overs + balls / 6.0)

    def record_match_result(
        self,
        team_a: str,
        team_b: str,
        runs_a: int,
        overs_a: float,
        wickets_a: int,
        runs_b: int,
        overs_b: float,
        wickets_b: int,
        winner_team: Optional[str] = None
    ):
        """Records match result, updates points (+2 Win, +1 Tie), and recalculates NRR."""
        self.register_team(team_a)
        self.register_team(team_b)

        entry_a = self.teams[team_a]
        entry_b = self.teams[team_b]

        entry_a.played += 1
        entry_b.played += 1

        # Calculate exact overs for NRR (all out = full quota assumed, e.g. 20.0)
        eff_overs_a = 20.0 if wickets_a == 10 else self._overs_to_decimal_balls(overs_a)
        eff_overs_b = 20.0 if wickets_b == 10 else self._overs_to_decimal_balls(overs_b)

        entry_a.runs_scored += runs_a
        entry_a.overs_faced += eff_overs_a
        entry_a.runs_conceded += runs_b
        entry_a.overs_bowled += eff_overs_b

        entry_b.runs_scored += runs_b
        entry_b.overs_faced += eff_overs_b
        entry_b.runs_conceded += runs_a
        entry_b.overs_bowled += eff_overs_a

        if winner_team == team_a:
            entry_a.won += 1
            entry_a.points += 2
            entry_b.lost += 1
        elif winner_team == team_b:
            entry_b.won += 1
            entry_b.points += 2
            entry_a.lost += 1
        else:
            entry_a.tied += 1
            entry_a.points += 1
            entry_b.tied += 1
            entry_b.points += 1

        # Update NRR
        entry_a.nrr = round(
            (entry_a.runs_scored / entry_a.overs_faced) - (entry_a.runs_conceded / entry_a.overs_bowled),
            3
        ) if entry_a.overs_faced > 0 and entry_a.overs_bowled > 0 else 0.0

        entry_b.nrr = round(
            (entry_b.runs_scored / entry_b.overs_faced) - (entry_b.runs_conceded / entry_b.overs_bowled),
            3
        ) if entry_b.overs_faced > 0 and entry_b.overs_bowled > 0 else 0.0

        logger.info(f"Recorded Match Result: Winner={winner_team}. Updated Standings for {team_a} & {team_b}")

    def get_standings(self) -> TournamentStandings:
        """Returns tournament points table sorted by points desc, then NRR desc."""
        sorted_list = sorted(
            self.teams.values(),
            key=lambda t: (t.points, t.nrr, t.won),
            reverse=True
        )
        return TournamentStandings(
            tournament_id=self.tournament_id,
            tournament_name=self.tournament_name,
            standings=sorted_list
        )
