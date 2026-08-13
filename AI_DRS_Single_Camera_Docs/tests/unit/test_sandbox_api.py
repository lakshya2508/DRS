"""
Unit tests for Interactive 3D Sandbox REST API Endpoints
"""

from fastapi.testclient import TestClient
import pytest

from ai_drs.api.main import app

client = TestClient(app)


def test_sandbox_viewer_api():
    resp = client.get("/api/v1/sandbox/viewer")
    assert resp.status_code == 200
    assert "3D HAWK-EYE CAMERA SANDBOX" in resp.text


def test_sandbox_seek_api():
    resp = client.post("/api/v1/sandbox/seek/M_SANDBOX_01?frame_index=250")
    assert resp.status_code == 200
    data = resp.json()

    assert data["current_frame"] == 250
    assert data["match_id"] == "M_SANDBOX_01"
