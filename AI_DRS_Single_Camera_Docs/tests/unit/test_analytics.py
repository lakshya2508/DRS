"""
Unit tests for Analytics Engine and REST API.
"""

import pytest
from fastapi.testclient import TestClient

from ai_drs.api.main import app
from ai_drs.analytics.analytics_engine import AnalyticsEngine, DeliveryRecord

client = TestClient(app)


def test_analytics_pitch_map():
    engine = AnalyticsEngine()
    data = engine.get_pitch_map(bowler_name="Jasprit Bumrah")
    assert len(data.deliveries) >= 3
    assert data.length_accuracy_pct > 0


def test_analytics_wagon_wheel():
    engine = AnalyticsEngine()
    data = engine.get_wagon_wheel(batter_name="Rohit Sharma")
    assert len(data.deliveries) >= 2
    assert "Mid Wicket" in data.runs_by_sector


def test_analytics_beehive():
    engine = AnalyticsEngine()
    data = engine.get_beehive(bowler_name="Jasprit Bumrah")
    assert len(data.deliveries) >= 3


def test_analytics_player_stats():
    engine = AnalyticsEngine()
    stats = engine.get_player_stats("Jasprit Bumrah")
    assert stats["player_name"] == "Jasprit Bumrah"
    assert stats["bowling"]["wickets"] >= 1


def test_analytics_api_pitch_map():
    res = client.get("/api/v1/analytics/pitch-map?bowler_name=Jasprit%20Bumrah")
    assert res.status_code == 200
    d = res.json()
    assert d["status"] == "ok"
    assert "pitch_map" in d


def test_analytics_api_wagon_wheel():
    res = client.get("/api/v1/analytics/wagon-wheel?batter_name=Virat%20Kohli")
    assert res.status_code == 200
    d = res.json()
    assert d["status"] == "ok"
    assert "wagon_wheel" in d


def test_analytics_api_beehive():
    res = client.get("/api/v1/analytics/beehive")
    assert res.status_code == 200
    d = res.json()
    assert d["status"] == "ok"


def test_analytics_api_player_stats():
    res = client.get("/api/v1/analytics/player/Rashid%20Khan")
    assert res.status_code == 200
    d = res.json()
    assert d["status"] == "ok"
    assert d["stats"]["player_name"] == "Rashid Khan"


def test_analytics_portal_html():
    res = client.get("/analytics")
    assert res.status_code == 200
    assert "Analytics Engine" in res.text
