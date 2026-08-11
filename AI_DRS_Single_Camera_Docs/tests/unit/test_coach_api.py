"""
Unit tests for AI Coach REST API Endpoints
"""

from fastapi.testclient import TestClient
import pytest

from ai_drs.api.main import app

client = TestClient(app)


def test_coach_briefing_api():
    resp = client.post("/api/v1/coach/briefing", json={
        "batter_name": "S. Smith",
        "situation_badge": "HIGH_PRESSURE",
        "primary_zone": "COVER"
    })
    assert resp.status_code == 200
    data = resp.json()

    assert "batter_profile" in data
    assert data["batter_profile"]["batter_name"] == "S. Smith"
    assert "recommended_field" in data
    assert data["recommended_field"]["tactical_plan_name"] == "ATTACKING_SLIP_CORDON"
