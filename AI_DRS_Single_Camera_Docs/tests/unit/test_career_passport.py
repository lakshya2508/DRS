"""
Unit tests for Global Player Passport & Career Records Engine Module
"""

import pytest

from ai_drs.enterprise.career_passport import (
    GlobalCareerPassportEngine,
    GlobalPlayerCareerPassport,
)


def test_global_career_passport_engine():
    engine = GlobalCareerPassportEngine()

    pid = "P_VK_18"
    pname = "Virat Kohli"

    # Match 1: 112 runs
    engine.record_match_performance(pid, pname, "India", runs_scored=112, wickets_taken=0)
    # Match 2: 54 runs
    engine.record_match_performance(pid, pname, "India", runs_scored=54, wickets_taken=1)

    passport = engine.get_or_create_passport(pid, pname, "India")

    assert isinstance(passport, GlobalPlayerCareerPassport)
    assert passport.player_name == "Virat Kohli"
    assert passport.matches_played == 2
    assert passport.total_runs == 166
    assert passport.centuries == 1
    assert passport.half_centuries == 1
    assert passport.highest_score == 112
    assert passport.total_wickets == 1
    assert passport.batting_average == 83.0
