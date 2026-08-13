"""
Authoritative Match State and Intelligence Data Models for AI DRS
"""

from typing import Dict, List, Optional
from pydantic import AliasChoices, BaseModel, Field



class TossState(BaseModel):
    """Schema representing toss outcome and innings setup."""
    toss_winner: str = Field(default="Team A", validation_alias=AliasChoices("toss_winner", "winner_team"))
    toss_choice: str = Field(default="BAT", description="'BAT' or 'BOWL'")
    batting_team: str = Field(default="Team A")
    bowling_team: str = Field(default="Team B")

    @property
    def winner_team(self) -> str:
        return self.toss_winner

    @property
    def decision(self) -> str:
        return self.toss_choice




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


from pydantic import AliasChoices, BaseModel, Field


class DeliveryEvent(BaseModel):
    """Validated delivery event input that updates MatchState."""
    delivery_id: str = Field(default="DEL_01")
    over_number: int = Field(default=0, ge=0)
    ball_number_in_over: int = Field(
        default=1, ge=1, le=6, validation_alias=AliasChoices("ball_number_in_over", "ball_number")
    )
    striker_name: str = Field(default="Batter A")
    non_striker_name: str = Field(default="Batter B")
    bowler_name: str = Field(default="Bowler A")
    runs_off_bat: int = Field(
        default=0, ge=0, validation_alias=AliasChoices("runs_off_bat", "runs_batter")
    )

    wide_runs: int = Field(default=0, ge=0)
    noball_runs: int = Field(default=0, ge=0)
    bye_runs: int = Field(default=0, ge=0)
    legbye_runs: int = Field(default=0, ge=0)
    is_wicket: bool = Field(default=False)
    wicket_type: Optional[str] = Field(
        default=None, validation_alias=AliasChoices("wicket_type", "dismissal_type")
    )
    dismissed_player: Optional[str] = Field(default=None)
    new_batsman_name: Optional[str] = Field(default=None)
    ball_speed_kmh: Optional[float] = Field(default=None)
    review_result: Optional[str] = Field(default=None)
    drs_review_requested: bool = Field(default=False)


    @property
    def ball_number(self) -> int:
        return self.ball_number_in_over

    @property
    def runs_batter(self) -> int:
        return self.runs_off_bat

    @property
    def dismissal_type(self) -> Optional[str]:
        return self.wicket_type



class MatchState(BaseModel):
    """Authoritative MatchState schema driving the entire platform."""
    match_id: str = Field(default="M_01")
    team_a: str = Field(default="Team A")
    team_b: str = Field(default="Team B")
    total_overs: int = Field(default=20, ge=1)
    innings: int = Field(default=1, ge=1, le=2)
    batting_team: str = Field(default="Team A")
    bowling_team: str = Field(default="Team B")
    score: int = Field(default=0, ge=0, validation_alias=AliasChoices("score", "runs"))
    wickets: int = Field(default=0, ge=0, le=10)
    total_legal_balls: int = Field(default=0, ge=0, validation_alias=AliasChoices("total_legal_balls", "legal_balls"))
    target: Optional[int] = Field(default=None, validation_alias=AliasChoices("target", "target_runs"))
    striker: BatsmanStats = Field(default_factory=lambda: BatsmanStats(name="Batter A"))
    non_striker: BatsmanStats = Field(default_factory=lambda: BatsmanStats(name="Batter B"))
    bowler: BowlerStats = Field(default_factory=lambda: BowlerStats(name="Bowler A"))
    current_over_runs: int = Field(default=0, ge=0)
    current_over_deliveries: List[str] = Field(default_factory=list)
    partnership: PartnershipStats = Field(default_factory=lambda: PartnershipStats(batsman_1="Batter A", batsman_2="Batter B"))
    current_run_rate: float = Field(default=0.0, ge=0.0)
    required_run_rate: Optional[float] = Field(default=None)
    runs_required: Optional[int] = Field(default=None)
    balls_remaining: int = Field(default=120, ge=0)
    wickets_remaining: int = Field(default=10, ge=0, le=10)
    toss: Optional[TossState] = Field(default=None)
    match_status: str = Field(default="IN_PROGRESS", description="'NOT_STARTED', 'IN_PROGRESS', 'COMPLETED', 'SUPER_OVER'")
    result_summary: Optional[str] = Field(default=None)

    @property
    def is_target_set(self) -> bool:
        return self.target is not None

    @property
    def target_runs(self) -> Optional[int]:
        return self.target

    @property
    def legal_balls(self) -> int:

        return self.total_legal_balls % 6

    @property
    def runs(self) -> int:
        return self.score

    @property
    def overs(self) -> float:
        return self.overs_formatted

    @property
    def overs_formatted(self) -> float:
        """Returns total innings overs in standard notation (e.g. 16.4)."""
        overs = self.total_legal_balls // 6
        balls = self.total_legal_balls % 6
        return float(f"{overs}.{balls}")


