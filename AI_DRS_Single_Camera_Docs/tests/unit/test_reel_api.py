"""
Unit tests for Viral Short-Form Video Exporter REST API Endpoints
"""

from fastapi.testclient import TestClient
import pytest

from ai_drs.api.main import app

client = TestClient(app)


def test_export_reel_api():
    resp = client.get("/api/v1/reels/export/DEL_14_2")
    assert resp.status_code == 200
    data = resp.json()

    assert data["aspect_ratio"] == "9:16"
    assert data["resolution"] == "1080x1920"
    assert "DEL_14_2" in data["download_url"]
