"""
Unit tests for Virtual Sponsorship & Commercial Ad REST API Endpoints
"""

from fastapi.testclient import TestClient
import pytest

from ai_drs.api.main import app

client = TestClient(app)


def test_ad_trigger_api():
    resp = client.get("/api/v1/ads/trigger/DRS_REVIEW")
    assert resp.status_code == 200
    data = resp.json()

    assert data["trigger_event"] == "DRS_REVIEW"
    assert data["duration_seconds"] == 6
    assert "AD_DRS_REVIEW" in data["ad_id"]
