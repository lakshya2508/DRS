"""
Authoritative Match State and Intelligence Data Models for AI DRS
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class TossState(BaseModel):
    """Schema representing toss outcome and innings setup."""
    toss_winner: str
    toss_choice: str = Field(description="'BAT' or 'BOWL'")
    batting_team: str
    bowling_team: str


class BatsmanStats(BaseModel):
    """Authoritative statistics for an individual batter."""
    name: str
    runs: int = Field(default=0, ge=0)
    balls: int = Field(default=0, ge=0)
    fours: int = Field(default=0, ge=0)
    sixes: int = Field(default=0, ge=0)
    dots: int = Field(default=0, ge=0)
    ones: int = Field(default=0, ge=0)
    twos: int = Field(default=0, ge=0)
    threes: int = Field(default=0, ge=0)
    strike_rate: float = Field(default=0.0, ge=0.0)
    boundary_percentage: float = Field(default=0.0, ge=0.0, le=100.0)
    dot_percentage: float = Field(default=0.0, ge=0.0, le=100.0)
    is_out: bool = Field(default=False)
    dismissal_info: Optional[str] = Field(default=None)

    def update_metrics(self):
        """Calculates derived metrics (strike rate, boundary %, dot %)."""
        if self.balls > 0:
            self.strike_rate = round((self.runs / self.balls) * 100.0, 2)
            self.dot_percentage = round((self.dots / self.balls) * 100.0, 2)
            self.boundary_percentage = round(((self.fours + self.sixes) / self.balls) * 100.0, 2)
        else:
            self.strike_rate = 0.0
            self.dot_percentage = 0.0
            self.boundary_percentage = 0.0


class BowlerStats(BaseModel):
    """Authoritative statistics for an individual bowler."""
    name: str
    legal_balls: int = Field(default=0, ge=0)
    runs_conceded: int = Field(default=0, ge=0)
    wickets: int = Field(default=0, ge=0)
    maidens: int = Field(default=0, ge=0)
    economy: float = Field(default=0.0, ge=0.0)
    dot_balls: int = Field(default=0, ge=0)
    speeds_kmh: List[float] = Field(default_factory=list)
    average_speed_kmh: float = Field(default=0.0, ge=0.0)
    maximum_speed_kmh: float = Field(default=0.0, ge=0.0)

    @property
    def overs_formatted(self) -> float:
        """Returns overs in standard cricket notation (e.g. 3.4 for 3 overs 4 balls)."""
        overs = self.legal_balls // 6
        balls = self.legal_balls % 6
        return float(f"{overs}.{balls}")

    def update_metrics(self):
        """Calculates economy rate and speed statistics."""
        total_overs = self.legal_balls / 6.0
        if total_overs > 0:
            self.economy = round(self.runs_conceded / total_overs, 2)
        else:
            self.economy = 0.0

        if self.speeds_kmh:
            self.average_speed_kmh = round(float(sum(self.speeds_kmh) / len(self.speeds_kmh)), 1)
            self.maximum_speed_kmh = round(float(max(self.speeds_kmh)), 1)


class PartnershipStats(BaseModel):
    """Current batting partnership statistics."""
    batsman_1: str
    batsman_2: str
    runs: int = Field(default=0, ge=0)
    balls: int = Field(default=0, ge=0)


class DeliveryEvent(BaseModel):
    """Validated delivery event input that updates MatchState."""
    delivery_id: str
    over_number: int = Field(ge=0)
    ball_number_in_over: int = Field(ge=1, le=6)
    striker_name: str
    non_striker_name: str
    bowler_name: str
    runs_off_bat: int = Field(default=0, ge=0)
    wide_runs: int = Field(default=0, ge=0)
    noball_runs: int = Field(default=0, ge=0)
    bye_runs: int = Field(default=0, ge=0)
    legbye_runs: int = Field(default=0, ge=0)
    is_wicket: bool = Field(default=False)
    wicket_type: Optional[str] = Field(default=None, description="'BOWLED', 'LBW', 'CAUGHT', 'RUN_OUT', 'STUMPED'")
    dismissed_player: Optional[str] = Field(default=None)
    new_batsman_name: Optional[str] = Field(default=None)
    ball_speed_kmh: Optional[float] = Field(default=None)
    review_result: Optional[str] = Field(default=None)


class MatchState(BaseModel):
    """Authoritative MatchState schema driving the entire platform."""
    match_id: str
    team_a: str
    team_b: str
    total_overs: int = Field(default=20, ge=1)
    innings: int = Field(default=1, ge=1, le=2)
    batting_team: str
    bowling_team: str
    score: int = Field(default=0, ge=0)
    wickets: int = Field(default=0, ge=0, le=10)
    total_legal_balls: int = Field(default=0, ge=0)
    target: Optional[int] = Field(default=None)
    striker: BatsmanStats
    non_striker: BatsmanStats
    bowler: BowlerStats
    current_over_runs: int = Field(default=0, ge=0)
    current_over_deliveries: List[str] = Field(default_factory=list)
    partnership: PartnershipStats
    current_run_rate: float = Field(default=0.0, ge=0.0)
    required_run_rate: Optional[float] = Field(default=None)
    runs_required: Optional[int] = Field(default=None)
    balls_remaining: int = Field(ge=0)
    wickets_remaining: int = Field(default=10, ge=0, le=10)
    toss: Optional[TossState] = Field(default=None)
    match_status: str = Field(default="IN_PROGRESS", description="'NOT_STARTED', 'IN_PROGRESS', 'COMPLETED', 'SUPER_OVER'")
    result_summary: Optional[str] = Field(default=None)

    @property
    def overs_formatted(self) -> float:
        """Returns total innings overs in standard notation (e.g. 16.4)."""
        overs = self.total_legal_balls // 6
        balls = self.total_legal_balls % 6
        return float(f"{overs}.{balls}")
