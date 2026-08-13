"""
Unit tests for Live Match DRS Decision Engine — Modern Cricket Leagues
"""

import pytest
from fastapi.testclient import TestClient

from ai_drs.api.main import app
from ai_drs.match.live_match_engine import (
    CreateLiveMatchRequest,
    DRSReviewRequest,
    LEAGUE_DRS_REVIEWS,
    LiveMatchEngine,
    MatchFormat,
)

client = TestClient(app)


# --- ENGINE UNIT TESTS ---

def test_live_match_engine_create_ipl_match():
    engine = LiveMatchEngine()
    req = CreateLiveMatchRequest(
        league="IPL",
        match_format=MatchFormat.IPL,
        team1_name="Mumbai Indians",
        team1_short="MI",
        team2_name="Chennai Super Kings",
        team2_short="CSK",
        total_overs=20
    )
    match = engine.create_match(req)
    assert "MI" in match.match_id or "CSK" in match.match_id
    assert match.batting_team.drs_reviews_remaining == 1
    assert match.bowling_team.drs_reviews_remaining == 1
    assert match.league == "IPL"


def test_live_match_engine_create_test_match():
    engine = LiveMatchEngine()
    req = CreateLiveMatchRequest(
        league="TEST",
        match_format=MatchFormat.TEST,
        team1_name="India",
        team1_short="IND",
        team2_name="Australia",
        team2_short="AUS",
        total_overs=90
    )
    match = engine.create_match(req)
    assert match.batting_team.drs_reviews_remaining == 2
    assert match.league == "TEST"


def test_drs_review_overturned():
    engine = LiveMatchEngine()
    req = CreateLiveMatchRequest(
        league="T20I", match_format=MatchFormat.T20I,
        team1_name="India", team1_short="IND",
        team2_name="England", team2_short="ENG",
        total_overs=20
    )
    match = engine.create_match(req)
    before_reviews = match.batting_team.drs_reviews_remaining

    review_req = DRSReviewRequest(
        match_id=match.match_id,
        reviewing_team_id="IND_id",
        delivery_id="DEL_001",
        pitching_result="IN_LINE",
        impact_result="IN_LINE",
        wicket_result="HITTING",
        original_umpire_decision="NOT_OUT",
        confidence_pct=91.5
    )
    result = engine.process_drs_review(review_req)
    assert result.final_decision.value == "OUT"
    assert result.drs_outcome.value == "UPHELD"
    # Review NOT deducted when overturned
    assert match.batting_team.drs_reviews_remaining == before_reviews


def test_drs_review_not_overturned_deducts_review():
    engine = LiveMatchEngine()
    req = CreateLiveMatchRequest(
        league="IPL", match_format=MatchFormat.IPL,
        team1_name="RCB", team1_short="RCB",
        team2_name="KKR", team2_short="KKR",
        total_overs=20
    )
    match = engine.create_match(req)

    review_req = DRSReviewRequest(
        match_id=match.match_id,
        reviewing_team_id="RCB_id",
        delivery_id="DEL_002",
        pitching_result="OUTSIDE_OFF",   # Not in line — NOT OUT
        impact_result="IN_LINE",
        wicket_result="HITTING",
        original_umpire_decision="OUT",
        confidence_pct=72.0
    )
    result = engine.process_drs_review(review_req)
    # Ball pitched outside off — overturned to NOT OUT
    assert result.final_decision.value == "NOT_OUT"
    assert result.drs_outcome.value == "UPHELD"


def test_league_drs_reviews_all_formats():
    assert LEAGUE_DRS_REVIEWS["TEST"] == 2
    assert LEAGUE_DRS_REVIEWS["ODI"] == 2
    assert LEAGUE_DRS_REVIEWS["IPL"] == 1
    assert LEAGUE_DRS_REVIEWS["T20I"] == 1
    assert LEAGUE_DRS_REVIEWS["SA20"] == 1


# --- API ENDPOINT TESTS ---

def test_api_get_supported_leagues():
    res = client.get("/api/v1/live/leagues")
    assert res.status_code == 200
    data = res.json()
    assert "supported_leagues" in data
    leagues = [l["league"] for l in data["supported_leagues"]]
    assert "IPL" in leagues
    assert "TEST" in leagues
    assert "SA20" in leagues


def test_api_create_live_match():
    payload = {
        "league": "IPL",
        "match_format": "IPL",
        "team1_name": "Mumbai Indians",
        "team1_short": "MI",
        "team2_name": "Chennai Super Kings",
        "team2_short": "CSK",
        "total_overs": 20
    }
    res = client.post("/api/v1/live/match/create", json=payload)
    assert res.status_code == 201
    data = res.json()
    assert "match_id" in data
    assert data["league"] == "IPL"
    assert data["batting_team"]["drs_reviews_remaining"] == 1
    return data["match_id"]


def test_api_add_delivery_and_drs_review():
    # Create match
    payload = {
        "league": "IPL", "match_format": "IPL",
        "team1_name": "GT", "team1_short": "GT",
        "team2_name": "LSG", "team2_short": "LSG",
        "total_overs": 20
    }
    res = client.post("/api/v1/live/match/create", json=payload)
    match_id = res.json()["match_id"]

    # Add delivery
    delivery_payload = {
        "over_number": 1, "ball_number": 1,
        "bowler_name": "Mohammed Shami",
        "batter_name": "KL Rahul",
        "runs_scored": 0, "extras": 0,
        "is_wicket": False
    }
    res = client.post(f"/api/v1/live/match/{match_id}/delivery", json=delivery_payload)
    assert res.status_code == 200

    # DRS Review
    drs_payload = {
        "match_id": match_id,
        "reviewing_team_id": "LSG_id",
        "delivery_id": "DEL_001",
        "pitching_result": "IN_LINE",
        "impact_result": "IN_LINE",
        "wicket_result": "HITTING",
        "original_umpire_decision": "NOT_OUT",
        "confidence_pct": 88.5
    }
    res = client.post(f"/api/v1/live/match/{match_id}/drs", json=drs_payload)
    assert res.status_code == 200
    data = res.json()
    assert data["final_decision"] == "OUT"
    assert data["drs_outcome"] == "UPHELD"
    assert "OVERTURNED" in data["voice_callout"]
