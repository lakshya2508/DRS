"""
Unit tests for Cricket League DB, Match Report Generator,
Ground Scoreboard and Leagues API endpoint.
"""

import pytest
from fastapi.testclient import TestClient

from ai_drs.api.main import app
from ai_drs.match.cricket_league_db import get_team, list_all_teams, IPL_TEAMS
from ai_drs.match.live_match_engine import (
    CreateLiveMatchRequest, DRSReviewRequest, LiveMatchEngine, MatchFormat
)
from ai_drs.reports.match_report_generator import MatchReportGenerator

client = TestClient(app)


# ── Cricket League DB ──────────────────────────────────────────────────────

def test_get_mi_team():
    team = get_team("MI")
    assert team.team_name == "Mumbai Indians"
    assert len(team.players) == 11
    names = [p.name for p in team.players]
    assert "Rohit Sharma" in names
    assert "Jasprit Bumrah" in names

def test_get_csk_team():
    team = get_team("CSK")
    assert team.team_name == "Chennai Super Kings"
    assert any(p.name == "MS Dhoni" for p in team.players)

def test_get_india_team():
    team = get_team("IND")
    assert team.short_name == "IND"
    assert any(p.name == "Virat Kohli" for p in team.players)

def test_list_all_teams():
    teams = list_all_teams()
    assert "MI" in teams
    assert "CSK" in teams
    assert "RCB" in teams
    assert len(teams) >= 10

def test_total_ipl_teams():
    assert len(IPL_TEAMS) == 10


# ── Match Report Generator ─────────────────────────────────────────────────

def _make_completed_match():
    engine = LiveMatchEngine()
    req = CreateLiveMatchRequest(
        league="IPL", match_format=MatchFormat.IPL,
        team1_name="Mumbai Indians", team1_short="MI",
        team2_name="Chennai Super Kings", team2_short="CSK",
        total_overs=20
    )
    match = engine.create_match(req)

    # Simulate a DRS review
    review_req = DRSReviewRequest(
        match_id=match.match_id,
        reviewing_team_id="MI_id",
        delivery_id="DEL_001",
        pitching_result="IN_LINE",
        impact_result="IN_LINE",
        wicket_result="HITTING",
        original_umpire_decision="NOT_OUT",
        confidence_pct=92.0
    )
    engine.process_drs_review(review_req)
    return match


def test_report_generator_json():
    match = _make_completed_match()
    gen   = MatchReportGenerator()
    report = gen.generate_json_report(match)

    assert "match_id" in report
    assert "drs_summary" in report
    assert report["drs_summary"]["total_reviews"] == 1
    assert report["drs_summary"]["overturned"] == 1
    assert report["drs_summary"]["overturn_rate_pct"] == 100.0


def test_report_generator_text():
    match = _make_completed_match()
    gen   = MatchReportGenerator()
    text  = gen.generate_text_summary(match)
    assert "AI DRS MATCH REPORT" in text
    assert "Mumbai Indians" in text
    assert "Overturned" in text


def test_report_save_json(tmp_path):
    match = _make_completed_match()
    gen   = MatchReportGenerator()
    path  = gen.save_json_report(match, output_dir=str(tmp_path))
    import json, os
    assert os.path.exists(path)
    data = json.loads(open(path).read())
    assert data["drs_summary"]["total_reviews"] == 1


# ── API Endpoints ──────────────────────────────────────────────────────────

def test_leagues_api():
    res = client.get("/api/v1/leagues")
    assert res.status_code == 200
    data = res.json()
    assert data["total_teams"] >= 10
    assert "MI" in data["teams"]
    assert "CSK" in data["teams"]
    assert "IND" in data["teams"]


def test_ground_scoreboard_serves():
    res = client.get("/scoreboard")
    assert res.status_code == 200
    assert "AI DRS" in res.text
    assert "Scoreboard" in res.text or "scoreboard" in res.text.lower()
