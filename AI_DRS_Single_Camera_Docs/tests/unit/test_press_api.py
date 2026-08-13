"""
Unit tests for Media Press Release REST API Endpoints
"""

from fastapi.testclient import TestClient
import pytest

from ai_drs.api.main import app

client = TestClient(app)


def test_press_release_api():
    resp = client.get("/api/v1/press/release/M_TEST_PRESS?player_of_match=R.+Sharma")
    assert resp.status_code == 200
    data = resp.json()

    assert "headline" in data
    assert "official_press_release_body" in data
    assert len(data["twitter_thread_posts"]) > 0
    assert "R. Sharma" in data["official_press_release_body"]
