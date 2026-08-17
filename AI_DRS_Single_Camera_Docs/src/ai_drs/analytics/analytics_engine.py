"""
Analytics Engine — Fulltrack.ai-style ball tracking, pitch maps, beehive heatmaps,
wagon wheels, and player performance metrics.
"""

import math
from dataclasses import dataclass, field, asdict
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel


class DeliveryRecord(BaseModel):
    delivery_id: str
    match_id: str
    over_num: int
    ball_num: int
    bowler_name: str
    bowler_type: str  # PACE / SPIN
    batter_name: str
    batter_hand: str  # RHB / LHB

    # Ball tracking metrics
    ball_speed_kmh: float        # e.g., 138.5
    release_height_m: float      # e.g., 2.15
    release_side_m: float        # e.g., -0.45 (left/right of stumps)
    bounce_pitch_x_m: float      # distance from center line (-1.5 to 1.5)
    bounce_pitch_y_m: float      # distance from stumps (0.0 to 20.12m)
    stump_impact_x_m: float      # horizontal offset at stump line (-0.5 to 0.5)
    stump_impact_z_m: float      # height at stump line (0.0 to 1.2m)
    swing_deg: float             # lateral movement in air (-3.0 to +3.0 deg)
    spin_rpm: float              # spin rate (e.g. 1800 rpm)

    # Shot & outcome metrics
    shot_sector_deg: float       # 0 to 360 degrees around field (0 = fine leg, 90 = cover)
    shot_distance_m: float       # distance shot traveled
    runs_scored: int             # 0, 1, 2, 3, 4, 6
    is_wicket: bool              # True / False
    wicket_type: Optional[str] = None  # BOWLED, LBW, CAUGHT, RUN_OUT
    length_zone: str             # YORKER, GOOD_LENGTH, SHORT, FULL_TOSS
    line_zone: str               # OFF_STUMP, MIDDLE_STUMP, LEG_STUMP, OUTSIDE_OFF, OUTSIDE_LEG


@dataclass
class PitchMapData:
    deliveries: List[Dict] = field(default_factory=list)
    good_length_count: int = 0
    yorker_count: int = 0
    short_count: int = 0
    full_toss_count: int = 0
    length_accuracy_pct: float = 0.0


@dataclass
class WagonWheelData:
    deliveries: List[Dict] = field(default_factory=list)
    runs_by_sector: Dict[str, int] = field(default_factory=dict)
    boundary_count_4s: int = 0
    boundary_count_6s: int = 0


@dataclass
class BeehiveData:
    deliveries: List[Dict] = field(default_factory=list)
    stump_hits_pct: float = 0.0
    above_stumps_pct: float = 0.0


class AnalyticsEngine:
    """Core analytics engine generating fulltrack.ai performance visualizations."""

    def __init__(self):
        self._records: List[DeliveryRecord] = []
        self._seed_demo_data()

    def add_delivery(self, record: DeliveryRecord) -> None:
        self._records.append(record)

    def filter_deliveries(
        self,
        bowler_name: Optional[str] = None,
        batter_name: Optional[str] = None,
        match_id: Optional[str] = None,
        bowler_type: Optional[str] = None,
        length_zone: Optional[str] = None,
    ) -> List[DeliveryRecord]:
        res = self._records
        if bowler_name:
            res = [r for r in res if r.bowler_name.lower() == bowler_name.lower()]
        if batter_name:
            res = [r for r in res if r.batter_name.lower() == batter_name.lower()]
        if match_id:
            res = [r for r in res if r.match_id == match_id]
        if bowler_type:
            res = [r for r in res if r.bowler_type.upper() == bowler_type.upper()]
        if length_zone:
            res = [r for r in res if r.length_zone.upper() == length_zone.upper()]
        return res

    def get_pitch_map(
        self, bowler_name: Optional[str] = None, match_id: Optional[str] = None
    ) -> PitchMapData:
        records = self.filter_deliveries(bowler_name=bowler_name, match_id=match_id)
        if not records:
            return PitchMapData()

        good = sum(1 for r in records if r.length_zone == "GOOD_LENGTH")
        yorker = sum(1 for r in records if r.length_zone == "YORKER")
        short = sum(1 for r in records if r.length_zone == "SHORT")
        full_toss = sum(1 for r in records if r.length_zone == "FULL_TOSS")
        acc = round((good + yorker) / len(records) * 100, 1)

        deliveries_dict = [r.model_dump() for r in records]
        return PitchMapData(
            deliveries=deliveries_dict,
            good_length_count=good,
            yorker_count=yorker,
            short_count=short,
            full_toss_count=full_toss,
            length_accuracy_pct=acc,
        )

    def get_wagon_wheel(
        self, batter_name: Optional[str] = None, match_id: Optional[str] = None
    ) -> WagonWheelData:
        records = self.filter_deliveries(batter_name=batter_name, match_id=match_id)
        if not records:
            return WagonWheelData()

        sectors = {
            "Fine Leg": 0, "Square Leg": 0, "Mid Wicket": 0, "Long On": 0,
            "Long Off": 0, "Cover": 0, "Point": 0, "Third Man": 0
        }
        fours = 0
        sixes = 0

        for r in records:
            deg = r.shot_sector_deg % 360
            if 0 <= deg < 45:
                sec = "Fine Leg"
            elif 45 <= deg < 90:
                sec = "Square Leg"
            elif 90 <= deg < 135:
                sec = "Mid Wicket"
            elif 135 <= deg < 180:
                sec = "Long On"
            elif 180 <= deg < 225:
                sec = "Long Off"
            elif 225 <= deg < 270:
                sec = "Cover"
            elif 270 <= deg < 315:
                sec = "Point"
            else:
                sec = "Third Man"

            sectors[sec] += r.runs_scored
            if r.runs_scored == 4:
                fours += 1
            elif r.runs_scored == 6:
                sixes += 1

        return WagonWheelData(
            deliveries=[r.model_dump() for r in records],
            runs_by_sector=sectors,
            boundary_count_4s=fours,
            boundary_count_6s=sixes,
        )

    def get_beehive(
        self, bowler_name: Optional[str] = None, match_id: Optional[str] = None
    ) -> BeehiveData:
        records = self.filter_deliveries(bowler_name=bowler_name, match_id=match_id)
        if not records:
            return BeehiveData()

        hits = sum(1 for r in records if -0.15 <= r.stump_impact_x_m <= 0.15 and 0.0 <= r.stump_impact_z_m <= 0.72)
        above = sum(1 for r in records if r.stump_impact_z_m > 0.72)
        hit_pct = round(hits / len(records) * 100, 1)
        above_pct = round(above / len(records) * 100, 1)

        return BeehiveData(
            deliveries=[r.model_dump() for r in records],
            stump_hits_pct=hit_pct,
            above_stumps_pct=above_pct,
        )

    def get_player_stats(self, player_name: str) -> dict:
        b_recs = [r for r in self._records if r.bowler_name.lower() == player_name.lower()]
        bat_recs = [r for r in self._records if r.batter_name.lower() == player_name.lower()]

        bowling_stats = {}
        if b_recs:
            total_balls = len(b_recs)
            avg_speed = sum(r.ball_speed_kmh for r in b_recs) / total_balls
            max_speed = max(r.ball_speed_kmh for r in b_recs)
            wickets = sum(1 for r in b_recs if r.is_wicket)
            runs_conceded = sum(r.runs_scored for r in b_recs)
            economy = round(runs_conceded / (total_balls / 6), 2) if total_balls >= 6 else 0.0
            bowling_stats = {
                "total_deliveries": total_balls,
                "wickets": wickets,
                "runs_conceded": runs_conceded,
                "economy_rate": economy,
                "average_speed_kmh": round(avg_speed, 1),
                "max_speed_kmh": round(max_speed, 1),
            }

        batting_stats = {}
        if bat_recs:
            total_runs = sum(r.runs_scored for r in bat_recs)
            dismissals = sum(1 for r in bat_recs if r.is_wicket)
            avg = round(total_runs / dismissals, 2) if dismissals > 0 else total_runs
            strike_rate = round(total_runs / len(bat_recs) * 100, 1)
            batting_stats = {
                "balls_faced": len(bat_recs),
                "runs_scored": total_runs,
                "average": avg,
                "strike_rate": strike_rate,
                "fours": sum(1 for r in bat_recs if r.runs_scored == 4),
                "sixes": sum(1 for r in bat_recs if r.runs_scored == 6),
            }

        return {
            "player_name": player_name,
            "bowling": bowling_stats,
            "batting": batting_stats,
        }

    def _seed_demo_data(self):
        """Pre-populates demo deliveries for instant analytics rendering."""
        demo_deliveries = [
            # Jasprit Bumrah vs Virat Kohli
            DeliveryRecord(
                delivery_id="DEL_101", match_id="MATCH_MIvRCB", over_num=1, ball_num=1,
                bowler_name="Jasprit Bumrah", bowler_type="PACE", batter_name="Virat Kohli", batter_hand="RHB",
                ball_speed_kmh=142.5, release_height_m=2.10, release_side_m=-0.30,
                bounce_pitch_x_m=0.10, bounce_pitch_y_m=5.20, stump_impact_x_m=0.05, stump_impact_z_m=0.45,
                swing_deg=-1.5, spin_rpm=0.0, shot_sector_deg=220, shot_distance_m=45.0,
                runs_scored=0, is_wicket=False, length_zone="GOOD_LENGTH", line_zone="MIDDLE_STUMP"
            ),
            DeliveryRecord(
                delivery_id="DEL_102", match_id="MATCH_MIvRCB", over_num=1, ball_num=2,
                bowler_name="Jasprit Bumrah", bowler_type="PACE", batter_name="Virat Kohli", batter_hand="RHB",
                ball_speed_kmh=145.0, release_height_m=2.12, release_side_m=-0.32,
                bounce_pitch_x_m=0.25, bounce_pitch_y_m=3.10, stump_impact_x_m=0.18, stump_impact_z_m=0.68,
                swing_deg=-2.0, spin_rpm=0.0, shot_sector_deg=260, shot_distance_m=72.0,
                runs_scored=4, is_wicket=False, length_zone="GOOD_LENGTH", line_zone="OUTSIDE_OFF"
            ),
            DeliveryRecord(
                delivery_id="DEL_103", match_id="MATCH_MIvRCB", over_num=1, ball_num=3,
                bowler_name="Jasprit Bumrah", bowler_type="PACE", batter_name="Virat Kohli", batter_hand="RHB",
                ball_speed_kmh=141.8, release_height_m=2.08, release_side_m=-0.28,
                bounce_pitch_x_m=0.00, bounce_pitch_y_m=1.80, stump_impact_x_m=0.02, stump_impact_z_m=0.15,
                swing_deg=0.5, spin_rpm=0.0, shot_sector_deg=160, shot_distance_m=15.0,
                runs_scored=0, is_wicket=True, wicket_type="BOWLED", length_zone="YORKER", line_zone="MIDDLE_STUMP"
            ),
            # Rashid Khan vs Rohit Sharma
            DeliveryRecord(
                delivery_id="DEL_201", match_id="MATCH_GTvMI", over_num=7, ball_num=1,
                bowler_name="Rashid Khan", bowler_type="SPIN", batter_name="Rohit Sharma", batter_hand="RHB",
                ball_speed_kmh=96.0, release_height_m=1.85, release_side_m=0.20,
                bounce_pitch_x_m=-0.15, bounce_pitch_y_m=4.80, stump_impact_x_m=-0.08, stump_impact_z_m=0.50,
                swing_deg=0.0, spin_rpm=2100.0, shot_sector_deg=110, shot_distance_m=85.0,
                runs_scored=6, is_wicket=False, length_zone="GOOD_LENGTH", line_zone="LEG_STUMP"
            ),
            DeliveryRecord(
                delivery_id="DEL_202", match_id="MATCH_GTvMI", over_num=7, ball_num=2,
                bowler_name="Rashid Khan", bowler_type="SPIN", batter_name="Rohit Sharma", batter_hand="RHB",
                ball_speed_kmh=98.5, release_height_m=1.87, release_side_m=0.22,
                bounce_pitch_x_m=0.05, bounce_pitch_y_m=4.50, stump_impact_x_m=0.02, stump_impact_z_m=0.40,
                swing_deg=0.0, spin_rpm=2250.0, shot_sector_deg=30, shot_distance_m=10.0,
                runs_scored=0, is_wicket=True, wicket_type="LBW", length_zone="GOOD_LENGTH", line_zone="MIDDLE_STUMP"
            ),
        ]
        for d in demo_deliveries:
            self.add_delivery(d)
