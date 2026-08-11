"""
Player Engines for AI DRS (Batsman and Bowler Statistics & Cricbuzz Live Cards)
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger
from ai_drs.match.models import BatsmanStats, BowlerStats, DeliveryEvent

logger = setup_logger("ai_drs.match.player")


class BatsmanCardPayload(BaseModel):
    """Cricbuzz-style Live Batter Card Payload."""
    name: str
    runs: int
    balls: int
    strike_rate: float
    fours: int
    sixes: int
    dot_percentage: float
    boundary_percentage: float
    is_out: bool
    dismissal_info: Optional[str] = None
    formatted_string: str


class BowlerCardPayload(BaseModel):
    """Cricbuzz-style Live Bowler Card Payload."""
    name: str
    overs_str: str
    maidens: int
    runs_conceded: int
    wickets: int
    economy: float
    dot_balls: int
    average_speed_kmh: float
    maximum_speed_kmh: float
    formatted_string: str


class BatsmanEngine:
    """Engine responsible for batter statistics tracking and Cricbuzz card rendering."""

    @staticmethod
    def update_stats(stats: BatsmanStats, delivery: DeliveryEvent) -> BatsmanStats:
        """Updates batter statistics from a validated delivery event."""
        if delivery.wide_runs == 0:
            stats.balls += 1

        stats.runs += delivery.runs_off_bat

        if delivery.runs_off_bat == 0 and delivery.wide_runs == 0 and delivery.noball_runs == 0:
            stats.dots += 1
        elif delivery.runs_off_bat == 1:
            stats.ones += 1
        elif delivery.runs_off_bat == 2:
            stats.twos += 1
        elif delivery.runs_off_bat == 3:
            stats.threes += 1
        elif delivery.runs_off_bat == 4:
            stats.fours += 1
        elif delivery.runs_off_bat == 6:
            stats.sixes += 1

        stats.update_metrics()
        return stats

    @staticmethod
    def get_cricbuzz_card(stats: BatsmanStats) -> BatsmanCardPayload:
        """Renders Cricbuzz-style live batter card."""
        fmt = (
            f"{stats.name}: {stats.runs} ({stats.balls}) | "
            f"SR: {stats.strike_rate:.2f} | 4s: {stats.fours}, 6s: {stats.sixes} | "
            f"Dot%: {stats.dot_percentage:.1f}%"
        )
        if stats.is_out and stats.dismissal_info:
            fmt += f" [{stats.dismissal_info}]"

        return BatsmanCardPayload(
            name=stats.name,
            runs=stats.runs,
            balls=stats.balls,
            strike_rate=stats.strike_rate,
            fours=stats.fours,
            sixes=stats.sixes,
            dot_percentage=stats.dot_percentage,
            boundary_percentage=stats.boundary_percentage,
            is_out=stats.is_out,
            dismissal_info=stats.dismissal_info,
            formatted_string=fmt
        )


class BowlerEngine:
    """Engine responsible for bowler statistics tracking and Cricbuzz card rendering."""

    @staticmethod
    def update_stats(
        stats: BowlerStats,
        delivery: DeliveryEvent,
        is_over_complete: bool = False,
        over_runs: int = 0
    ) -> BowlerStats:
        """Updates bowler statistics from a validated delivery event."""
        is_legal = (delivery.wide_runs == 0 and delivery.noball_runs == 0)
        conceded = delivery.runs_off_bat + delivery.wide_runs + delivery.noball_runs

        stats.runs_conceded += conceded
        if is_legal:
            stats.legal_balls += 1
            if (delivery.runs_off_bat + delivery.wide_runs + delivery.noball_runs + delivery.bye_runs + delivery.legbye_runs) == 0:
                stats.dot_balls += 1

        if delivery.is_wicket and delivery.wicket_type != "RUN_OUT":
            stats.wickets += 1

        if delivery.ball_speed_kmh is not None:
            stats.speeds_kmh.append(delivery.ball_speed_kmh)

        if is_over_complete and over_runs == 0:
            stats.maidens += 1

        stats.update_metrics()
        return stats

    @staticmethod
    def get_cricbuzz_card(stats: BowlerStats) -> BowlerCardPayload:
        """Renders Cricbuzz-style live bowler card."""
        overs_str = f"{stats.legal_balls // 6}.{stats.legal_balls % 6}"
        figure = f"{stats.legal_balls // 6}-{stats.maidens}-{stats.runs_conceded}-{stats.wickets}"

        fmt = (
            f"{stats.name}: {figure} (Overs {overs_str}) | "
            f"Econ: {stats.economy:.2f} | Avg Speed: {stats.average_speed_kmh:.1f} km/h | "
            f"Max Speed: {stats.maximum_speed_kmh:.1f} km/h"
        )

        return BowlerCardPayload(
            name=stats.name,
            overs_str=overs_str,
            maidens=stats.maidens,
            runs_conceded=stats.runs_conceded,
            wickets=stats.wickets,
            economy=stats.economy,
            dot_balls=stats.dot_balls,
            average_speed_kmh=stats.average_speed_kmh,
            maximum_speed_kmh=stats.maximum_speed_kmh,
            formatted_string=fmt
        )
