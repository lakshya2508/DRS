"""
Unit tests for Front-Foot No-Ball & Tramline Wide Detection Engine Module
"""

import pytest

from ai_drs.events.crease_checker import CreaseCheckResult, CreaseCheckerEngine


def test_crease_checker_no_ball_and_wide():
    checker = CreaseCheckerEngine()

    # 1. Front-foot Overstep No-Ball
    res_noball = checker.evaluate_delivery_legality(front_toe_y_m=0.03, ball_bounce_x_m=0.0)
    assert isinstance(res_noball, CreaseCheckResult)
    assert res_noball.is_front_foot_no_ball is True
    assert res_noball.front_foot_overstep_m == 0.03
    assert res_noball.is_wide_ball is False

    # 2. Off-side Wide
    res_offwide = checker.evaluate_delivery_legality(front_toe_y_m=-0.10, ball_bounce_x_m=-1.05)
    assert res_offwide.is_front_foot_no_ball is False
    assert res_offwide.is_wide_ball is True
    assert res_offwide.wide_line_type == "OFF_SIDE_WIDE"

    # 3. Leg-side Wide
    res_legwide = checker.evaluate_delivery_legality(front_toe_y_m=-0.10, ball_bounce_x_m=0.60)
    assert res_legwide.is_wide_ball is True
    assert res_legwide.wide_line_type == "LEG_SIDE_WIDE"

    # 4. Legal Delivery
    res_legal = checker.evaluate_delivery_legality(front_toe_y_m=-0.05, ball_bounce_x_m=0.10)
    assert res_legal.is_front_foot_no_ball is False
    assert res_legal.is_wide_ball is False
