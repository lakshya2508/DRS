"""
Tournament Leaderboards & Player Honors Module (Orange Cap & Purple Cap)
"""

from typing import Dict, List
from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.tournament.leaderboards")


class PlayerLeaderboardStats(BaseModel):
    """Schema representing player tournament leaderboard stats."""
    player_name: str
    team_name: str
    runs: int = 0
    balls_faced: int = 0
    fours: int = 0
    sixes: int = 0
    wickets: int = 0
    overs_bowled: float = 0.0
    runs_conceded: int = 0

    @property
    def strike_rate(self) -> float:
        return round((self.runs / self.balls_faced * 100.0), 2) if self.balls_faced > 0 else 0.0

    @property
    def bowling_economy(self) -> float:
        return round((self.runs_conceded / self.overs_bowled), 2) if self.overs_bowled > 0 else 0.0


class TournamentLeaderboardPackage(BaseModel):
    """Schema representing full tournament honors package."""
    tournament_id: str
    orange_cap_holder: Optional[PlayerLeaderboardStats] = None  # Most Runs
    purple_cap_holder: Optional[PlayerLeaderboardStats] = None  # Most Wickets
    most_sixes_holder: Optional[PlayerLeaderboardStats] = None
    all_players: List[PlayerLeaderboardStats] = Field(default_factory=list)


class LeaderboardEngine:
    """Computes tournament individual player leaderboards and honors."""

    def __init__(self, tournament_id: str):
        self.tournament_id = tournament_id
        self.players: Dict[str, PlayerLeaderboardStats] = {}

    def update_player_batting(self, player_name: str, team_name: str, runs: int, balls: int, fours: int = 0, sixes: int = 0):
        """Updates cumulative batting stats for a player."""
        if player_name not in self.players:
            self.players[player_name] = PlayerLeaderboardStats(player_name=player_name, team_name=team_name)

        p = self.players[player_name]
        p.runs += runs
        p.balls_faced += balls
        p.fours += fours
        p.sixes += sixes

    def update_player_bowling(self, player_name: str, team_name: str, wickets: int, overs: float, runs_conceded: int):
        """Updates cumulative bowling stats for a player."""
        if player_name not in self.players:
            self.players[player_name] = PlayerLeaderboardStats(player_name=player_name, team_name=team_name)

        p = self.players[player_name]
        p.wickets += wickets
        p.overs_bowled += overs
        p.runs_conceded += runs_conceded

    def get_leaderboards(self) -> TournamentLeaderboardPackage:
        """Returns orange cap, purple cap, most sixes, and sorted player rankings."""
        all_p = list(self.players.values())
        if not all_p:
            return TournamentLeaderboardPackage(tournament_id=self.tournament_id)

        orange_cap = max(all_p, key=lambda p: (p.runs, p.strike_rate)) if any(p.runs > 0 for p in all_p) else None
        purple_cap = max(all_p, key=lambda p: (p.wickets, -p.bowling_economy)) if any(p.wickets > 0 for p in all_p) else None
        most_sixes = max(all_p, key=lambda p: p.sixes) if any(p.sixes > 0 for p in all_p) else None

        logger.info(
            f"Leaderboard [{self.tournament_id}]: Orange Cap={orange_cap.player_name if orange_cap else 'N/A'}, "
            f"Purple Cap={purple_cap.player_name if purple_cap else 'N/A'}"
        )

        return TournamentLeaderboardPackage(
            tournament_id=self.tournament_id,
            orange_cap_holder=orange_cap,
            purple_cap_holder=purple_cap,
            most_sixes_holder=most_sixes,
            all_players=sorted(all_p, key=lambda p: p.runs, reverse=True)
        )
