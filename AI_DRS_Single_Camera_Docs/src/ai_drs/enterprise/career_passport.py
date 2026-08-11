"""
Global Player Passport & Career Records Engine for Multi-Tournament Federation
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.enterprise.career")


class GlobalPlayerCareerPassport(BaseModel):
    """Schema representing global player career stats across all tournaments and leagues."""
    player_id: str
    player_name: str
    country: str
    matches_played: int = 0
    total_runs: int = 0
    centuries: int = 0
    half_centuries: int = 0
    highest_score: int = 0
    total_wickets: int = 0
    five_wicket_hauls: int = 0
    best_bowling_wickets: int = 0
    total_catches: int = 0

    @property
    def batting_average(self) -> float:
        return round(float(self.total_runs / self.matches_played), 2) if self.matches_played > 0 else 0.0


class GlobalCareerPassportEngine:
    """Aggregates player career records across multi-tournament federations."""

    def __init__(self):
        self.passports: Dict[str, GlobalPlayerCareerPassport] = {}

    def get_or_create_passport(self, player_id: str, player_name: str, country: str) -> GlobalPlayerCareerPassport:
        """Retrieves or creates global player career passport."""
        if player_id not in self.passports:
            self.passports[player_id] = GlobalPlayerCareerPassport(
                player_id=player_id,
                player_name=player_name,
                country=country
            )
        return self.passports[player_id]

    def record_match_performance(
        self,
        player_id: str,
        player_name: str,
        country: str,
        runs_scored: int = 0,
        wickets_taken: int = 0,
        catches_taken: int = 0
    ):
        """Updates career stats after a match."""
        p = self.get_or_create_passport(player_id, player_name, country)
        p.matches_played += 1
        p.total_runs += runs_scored
        p.total_wickets += wickets_taken
        p.total_catches += catches_taken

        if runs_scored >= 100:
            p.centuries += 1
        elif runs_scored >= 50:
            p.half_centuries += 1

        if runs_scored > p.highest_score:
            p.highest_score = runs_scored

        if wickets_taken >= 5:
            p.five_wicket_hauls += 1

        if wickets_taken > p.best_bowling_wickets:
            p.best_bowling_wickets = wickets_taken

        logger.info(
            f"Updated Career Passport [{player_name}]: {p.matches_played} matches, "
            f"{p.total_runs} runs, {p.total_wickets} wickets."
        )


# Global career passport engine instance
career_engine = GlobalCareerPassportEngine()
