"""
Unit tests for AI Pitch Curator REST API Endpoints
"""

from fastapi.testclient import TestClient
import pytest

from ai_drs.api.main import app

client = TestClient(app)


def test_curator_report_api():
    resp = client.get("/api/v1/curator/report")
    assert resp.status_code == 200
    data = resp.json()

    assert "moisture_pct" in data
    assert "grass_coverage_pct" in data
    assert "max_crack_width_mm" in data
    assert "pitch_condition_label" in data
