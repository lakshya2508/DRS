"""
Unit tests for BatsmanEngine and BowlerEngine
"""

import pytest

from ai_drs.match.models import BatsmanStats, BowlerStats, DeliveryEvent
from ai_drs.match.player_engines import (
    BatsmanEngine,
    BowlerEngine,
    BatsmanCardPayload,
    BowlerCardPayload,
)


def test_batsman_engine_updates_and_cricbuzz_card():
    stats = BatsmanStats(name="V. Kohli")

    # Delivery 1: 4 runs
    d1 = DeliveryEvent(
        delivery_id="D1", over_number=0, ball_number_in_over=1,
        striker_name="V. Kohli", non_striker_name="R. Sharma", bowler_name="M. Starc",
        runs_off_bat=4
    )
    BatsmanEngine.update_stats(stats, d1)

    # Delivery 2: 6 runs
    d2 = DeliveryEvent(
        delivery_id="D2", over_number=0, ball_number_in_over=2,
        striker_name="V. Kohli", non_striker_name="R. Sharma", bowler_name="M. Starc",
        runs_off_bat=6
    )
    BatsmanEngine.update_stats(stats, d2)

    assert stats.runs == 10
    assert stats.balls == 2
    assert stats.fours == 1
    assert stats.sixes == 1
    assert stats.strike_rate == 500.0
    assert stats.boundary_percentage == 100.0

    card = BatsmanEngine.get_cricbuzz_card(stats)
    assert isinstance(card, BatsmanCardPayload)
    assert "V. Kohli: 10 (2)" in card.formatted_string
    assert "4s: 1, 6s: 1" in card.formatted_string


def test_bowler_engine_updates_maiden_and_speeds():
    stats = BowlerStats(name="Jasprit Bumrah")

    # 6 dot balls in over
    for i in range(1, 7):
        d = DeliveryEvent(
            delivery_id=f"D{i}", over_number=0, ball_number_in_over=i,
            striker_name="V. Kohli", non_striker_name="R. Sharma", bowler_name="Jasprit Bumrah",
            runs_off_bat=0, ball_speed_kmh=140.0 + i
        )
        BowlerEngine.update_stats(stats, d, is_over_complete=(i == 6), over_runs=0)

    assert stats.legal_balls == 6
    assert stats.runs_conceded == 0
    assert stats.maidens == 1
    assert stats.economy == 0.0
    assert stats.dot_balls == 6
    assert stats.maximum_speed_kmh == 146.0
    assert stats.average_speed_kmh == 143.5

    card = BowlerEngine.get_cricbuzz_card(stats)
    assert isinstance(card, BowlerCardPayload)
    assert "Jasprit Bumrah: 1-1-0-0" in card.formatted_string
    assert "Max Speed: 146.0 km/h" in card.formatted_string
