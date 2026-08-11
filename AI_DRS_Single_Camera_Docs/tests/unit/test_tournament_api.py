"""
Unit tests for Tournament REST API Endpoints
"""

from fastapi.testclient import TestClient
import pytest

from ai_drs.api.main import app

client = TestClient(app)


def test_tournament_api_e2e():
    t_id = "T_API_2026"

    # 1. Create Tournament
    resp_create = client.post("/api/v1/tournament/create", json={
        "tournament_id": t_id,
        "tournament_name": "World Cup 2026",
        "teams": ["India", "Australia", "England"]
    })
    assert resp_create.status_code == 201
    data_create = resp_create.json()
    assert data_create["tournament_id"] == t_id
    assert len(data_create["standings"]) == 3

    # 2. Record Match Result
    resp_match = client.post(f"/api/v1/tournament/{t_id}/match-result", json={
        "team_a": "India",
        "team_b": "Australia",
        "runs_a": 200,
        "overs_a": 20.0,
        "wickets_a": 3,
        "runs_b": 170,
        "overs_b": 20.0,
        "wickets_b": 9,
        "winner_team": "India"
    })
    assert resp_match.status_code == 200
    data_match = resp_match.json()
    assert data_match["standings"][0]["team_name"] == "India"
    assert data_match["standings"][0]["points"] == 2
    assert data_match["standings"][0]["nrr"] == 1.5

    # 3. Get Standings
    resp_standings = client.get(f"/api/v1/tournament/{t_id}/standings")
    assert resp_standings.status_code == 200

    # 4. Get Leaderboards
    resp_lead = client.get(f"/api/v1/tournament/{t_id}/leaderboards")
    assert resp_lead.status_code == 200
