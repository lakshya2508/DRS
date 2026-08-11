"""
Unit tests for Wagon Wheel Shot Direction Estimator Module
"""

import pytest

from ai_drs.analytics.wagon_wheel import (
    ShotZone,
    WagonWheelEngine,
    WagonWheelShot,
)


def test_wagon_wheel_computation_and_classification():
    engine = WagonWheelEngine()

    # Cover Drive (dx=-30m, dy=30m -> ~315 deg)
    shot_cover = engine.compute_shot("DEL_01", "V. Kohli", dx_m=-30.0, dy_m=30.0, runs=4)
    assert isinstance(shot_cover, WagonWheelShot)
    assert shot_cover.zone == ShotZone.COVER
    assert shot_cover.runs == 4

    # Long On (dx=10m, dy=40m -> ~14 deg)
    shot_longon = engine.compute_shot("DEL_02", "V. Kohli", dx_m=10.0, dy_m=40.0, runs=6)
    assert shot_longon.zone == ShotZone.LONG_ON
    assert shot_longon.runs == 6


def test_batter_wagon_wheel_summary():
    engine = WagonWheelEngine()
    shots = [
        engine.compute_shot("D1", "Batter A", dx_m=-30.0, dy_m=30.0, runs=4),
        engine.compute_shot("D2", "Batter A", dx_m=-40.0, dy_m=40.0, runs=4),
        engine.compute_shot("D3", "Batter A", dx_m=10.0, dy_m=40.0, runs=6),
    ]

    summary = engine.summarize_batter_wagon_wheel(shots)
    assert summary["COVER"] == 8
    assert summary["LONG_ON"] == 6
    assert summary["FINE_LEG"] == 0
