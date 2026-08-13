"""
Live Match Engine — Real-time ball-by-ball DRS decision processing
for modern cricket leagues: IPL, T20I, ODI, Test Match.
"""

import uuid
import time
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.match.live_match_engine")


# --- ENUMS ---

class MatchFormat(str, Enum):
    TEST   = "TEST"       # 2 DRS reviews per team per innings
    ODI    = "ODI"        # 2 DRS reviews per team per innings
    T20    = "T20"        # 1 DRS review per team per innings
    T20I   = "T20I"       # 1 DRS review per team per innings
    IPL    = "IPL"        # 1 DRS review per team per innings
    THE_HUNDRED = "THE_HUNDRED"  # 1 DRS review per team per innings
    WPL    = "WPL"        # 1 DRS review per team per innings
    SA20   = "SA20"       # 1 DRS review per team per innings
    BBL    = "BBL"        # 1 DRS review per team per innings
    CPL    = "CPL"        # 1 DRS review per team per innings

class LiveMatchStatus(str, Enum):
    SCHEDULED  = "SCHEDULED"
    IN_PROGRESS = "IN_PROGRESS"
    INNINGS_BREAK = "INNINGS_BREAK"
    RAIN_DELAY = "RAIN_DELAY"
    COMPLETED  = "COMPLETED"

class DRSOutcome(str, Enum):
    UPHELD     = "UPHELD"       # Review succeeded — review NOT deducted (overturned)
    RETAINED   = "RETAINED"     # Review lost — review deducted
    PENDING    = "PENDING"      # Under review
    NO_REVIEW  = "NO_REVIEW"    # Not challenged

class LBWDecision(str, Enum):
    OUT          = "OUT"
    NOT_OUT      = "NOT_OUT"
    INCONCLUSIVE = "INCONCLUSIVE"


# --- DATA MODELS ---

class LiveTeam(BaseModel):
    team_id: str
    team_name: str
    short_name: str           # e.g. "MI", "CSK", "IND"
    drs_reviews_remaining: int
    drs_reviews_total: int

class LivePlayer(BaseModel):
    player_id: str
    name: str
    role: str                 # BATTER / BOWLER / ALL_ROUNDER / WK_BATTER
    batting_style: str        # RIGHT_HAND / LEFT_HAND
    bowling_style: str        # RIGHT_ARM_FAST / LEFT_ARM_SPIN etc.

class LiveDelivery(BaseModel):
    delivery_id: str = Field(default_factory=lambda: str(uuid.uuid4())[:8])
    over_number: int
    ball_number: int
    bowler_name: str
    batter_name: str
    runs_scored: int = 0
    extras: int = 0
    is_wicket: bool = False
    wicket_type: Optional[str] = None
    drs_outcome: DRSOutcome = DRSOutcome.NO_REVIEW
    lbw_decision: Optional[LBWDecision] = None
    pitching_zone: Optional[str] = None     # IN_LINE / OUTSIDE_OFF / OUTSIDE_LEG
    impact_zone: Optional[str] = None       # IN_LINE / UMPIRES_CALL / MISSING
    wicket_zone: Optional[str] = None       # HITTING / UMPIRES_CALL / MISSING
    ball_speed_kmh: Optional[float] = None
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class DRSReviewRequest(BaseModel):
    match_id: str
    reviewing_team_id: str
    delivery_id: str
    pitching_result: str = Field(default="IN_LINE", description="IN_LINE / OUTSIDE_OFF / OUTSIDE_LEG")
    impact_result: str = Field(default="IN_LINE", description="IN_LINE / UMPIRES_CALL / MISSING")
    wicket_result: str = Field(default="HITTING", description="HITTING / UMPIRES_CALL / MISSING")
    original_umpire_decision: str = Field(default="NOT_OUT", description="OUT / NOT_OUT")
    confidence_pct: float = Field(default=85.0)

class DRSReviewResult(BaseModel):
    review_id: str
    match_id: str
    delivery_id: str
    reviewing_team: str
    original_decision: str
    final_decision: LBWDecision
    drs_outcome: DRSOutcome
    reviews_remaining: int
    pitching: str
    impact: str
    wickets: str
    confidence_pct: float
    voice_callout: str
    timestamp: str

class LiveMatchState(BaseModel):
    match_id: str
    league: str
    match_format: MatchFormat
    status: LiveMatchStatus
    batting_team: LiveTeam
    bowling_team: LiveTeam
    current_over: int
    current_ball: int
    total_overs: int
    batting_score: int
    batting_wickets: int
    bowling_score: int
    bowling_wickets: int
    target: Optional[int] = None
    deliveries: List[LiveDelivery] = []
    drs_reviews_log: List[DRSReviewResult] = []
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    last_updated: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class CreateLiveMatchRequest(BaseModel):
    league: str = Field(default="IPL", description="IPL / T20I / ODI / TEST / THE_HUNDRED / SA20 / BBL / CPL")
    match_format: MatchFormat = MatchFormat.IPL
    team1_name: str = Field(default="Mumbai Indians")
    team1_short: str = Field(default="MI")
    team2_name: str = Field(default="Chennai Super Kings")
    team2_short: str = Field(default="CSK")
    total_overs: int = Field(default=20, ge=1, le=90)


# --- LEAGUE DRS REVIEW RULES ---

LEAGUE_DRS_REVIEWS: Dict[str, int] = {
    "TEST":         2,
    "ODI":          2,
    "T20":          1,
    "T20I":         1,
    "IPL":          1,
    "THE_HUNDRED":  1,
    "WPL":          1,
    "SA20":         1,
    "BBL":          1,
    "CPL":          1,
}


# --- LIVE MATCH ENGINE ---

class LiveMatchEngine:
    """Real-time ball-by-ball live match engine for modern cricket leagues."""

    def __init__(self):
        self._matches: Dict[str, LiveMatchState] = {}

    def create_match(self, req: CreateLiveMatchRequest) -> LiveMatchState:
        """Creates a new live match session with DRS review budgets."""
        match_id = f"MATCH_{req.team1_short}v{req.team2_short}_{str(uuid.uuid4())[:6].upper()}"
        reviews = LEAGUE_DRS_REVIEWS.get(req.league.upper(), 1)

        batting_team = LiveTeam(
            team_id=f"{req.team1_short}_id",
            team_name=req.team1_name,
            short_name=req.team1_short,
            drs_reviews_remaining=reviews,
            drs_reviews_total=reviews
        )
        bowling_team = LiveTeam(
            team_id=f"{req.team2_short}_id",
            team_name=req.team2_name,
            short_name=req.team2_short,
            drs_reviews_remaining=reviews,
            drs_reviews_total=reviews
        )

        match = LiveMatchState(
            match_id=match_id,
            league=req.league.upper(),
            match_format=req.match_format,
            status=LiveMatchStatus.IN_PROGRESS,
            batting_team=batting_team,
            bowling_team=bowling_team,
            current_over=1,
            current_ball=0,
            total_overs=req.total_overs,
            batting_score=0,
            batting_wickets=0,
            bowling_score=0,
            bowling_wickets=0,
        )
        self._matches[match_id] = match
        logger.info(f"Live match created: {match_id} ({req.league}, {req.team1_short} vs {req.team2_short})")
        return match

    def get_match(self, match_id: str) -> Optional[LiveMatchState]:
        return self._matches.get(match_id)

    def list_matches(self) -> List[LiveMatchState]:
        return list(self._matches.values())

    def add_delivery(self, match_id: str, delivery: LiveDelivery) -> LiveMatchState:
        """Records a new ball delivery to the live match state."""
        match = self._matches.get(match_id)
        if not match:
            raise ValueError(f"Match '{match_id}' not found.")

        match.deliveries.append(delivery)
        match.batting_score += delivery.runs_scored + delivery.extras
        if delivery.is_wicket:
            match.batting_wickets += 1

        # Advance ball/over counter
        match.current_ball += 1
        if match.current_ball > 6:
            match.current_ball = 1
            match.current_over += 1

        match.last_updated = datetime.utcnow().isoformat()
        logger.info(f"Delivery recorded: {match_id} — Over {delivery.over_number}.{delivery.ball_number} by {delivery.bowler_name}")
        return match

    def process_drs_review(self, req: DRSReviewRequest) -> DRSReviewResult:
        """Processes a live DRS review request and returns final LBW decision."""
        match = self._matches.get(req.match_id)
        if not match:
            raise ValueError(f"Match '{req.match_id}' not found.")

        # Identify reviewing team
        if match.batting_team.team_id == req.reviewing_team_id or \
           match.batting_team.short_name.lower() in req.reviewing_team_id.lower():
            reviewing_team = match.batting_team
        else:
            reviewing_team = match.bowling_team

        if reviewing_team.drs_reviews_remaining <= 0:
            raise ValueError(f"Team '{reviewing_team.team_name}' has no DRS reviews remaining.")

        # --- Apply ICC LBW 3-Zone Decision Logic ---
        pitching_ok = req.pitching_result == "IN_LINE"
        impact_ok = req.impact_result in ("IN_LINE", "UMPIRES_CALL")
        hitting_ok = req.wicket_result in ("HITTING", "UMPIRES_CALL")

        if pitching_ok and impact_ok and hitting_ok:
            final_decision = LBWDecision.OUT
        elif not pitching_ok:
            final_decision = LBWDecision.NOT_OUT  # Outside line of stumps — not out
        elif req.impact_result == "MISSING" or req.wicket_result == "MISSING":
            final_decision = LBWDecision.NOT_OUT
        else:
            final_decision = LBWDecision.INCONCLUSIVE

        # Determine if review is overturned
        overturned = (final_decision.value != req.original_umpire_decision)
        if overturned:
            drs_outcome = DRSOutcome.UPHELD          # Review succeeded — not deducted
            voice_callout = f"DECISION OVERTURNED — THIRD UMPIRE SAYS {final_decision.value}!"
        else:
            drs_outcome = DRSOutcome.RETAINED        # Review failed — deduct
            reviewing_team.drs_reviews_remaining -= 1
            voice_callout = (
                f"DECISION STANDS — {req.original_umpire_decision}. "
                f"{reviewing_team.short_name} has {reviewing_team.drs_reviews_remaining} review(s) left."
            )

        review_result = DRSReviewResult(
            review_id=f"DRS_{str(uuid.uuid4())[:8].upper()}",
            match_id=req.match_id,
            delivery_id=req.delivery_id,
            reviewing_team=reviewing_team.team_name,
            original_decision=req.original_umpire_decision,
            final_decision=final_decision,
            drs_outcome=drs_outcome,
            reviews_remaining=reviewing_team.drs_reviews_remaining,
            pitching=req.pitching_result,
            impact=req.impact_result,
            wickets=req.wicket_result,
            confidence_pct=round(req.confidence_pct, 1),
            voice_callout=voice_callout,
            timestamp=datetime.utcnow().isoformat()
        )

        match.drs_reviews_log.append(review_result)
        match.last_updated = datetime.utcnow().isoformat()
        logger.info(f"DRS Review processed: {req.match_id} — {final_decision.value} ({drs_outcome.value})")
        return review_result

    def get_drs_budget(self, match_id: str) -> Dict:
        """Returns current DRS review budget for both teams."""
        match = self._matches.get(match_id)
        if not match:
            raise ValueError(f"Match '{match_id}' not found.")
        return {
            match.batting_team.team_name: {
                "remaining": match.batting_team.drs_reviews_remaining,
                "total": match.batting_team.drs_reviews_total
            },
            match.bowling_team.team_name: {
                "remaining": match.bowling_team.drs_reviews_remaining,
                "total": match.bowling_team.drs_reviews_total
            }
        }
