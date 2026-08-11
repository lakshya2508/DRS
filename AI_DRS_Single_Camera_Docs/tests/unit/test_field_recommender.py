"""
Unit tests for Bowler Tactical Field Setting Recommendation Engine Module
"""

import pytest

from ai_drs.ai_coach.field_recommender import (
    FieldPosition,
    FieldRecommenderEngine,
    TacticalFieldSetting,
)


def test_field_recommender_attacking():
    setting = FieldRecommenderEngine.recommend_field_setting(situation_badge="CRITICAL", batter_primary_zone="COVER")

    assert isinstance(setting, TacticalFieldSetting)
    assert setting.tactical_plan_name == "ATTACKING_SLIP_CORDON"
    assert setting.catchers_count == 3
    assert len(setting.field_positions) == 9
    assert any(p.position_name == "First Slip" for p in setting.field_positions)


def test_field_recommender_containment():
    setting = FieldRecommenderEngine.recommend_field_setting(situation_badge="STABLE", batter_primary_zone="MIDWICKET")

    assert setting.tactical_plan_name == "BALANCED_CONTAINMENT"
    assert setting.boundary_fielders_count == 5
    assert len(setting.field_positions) == 9
