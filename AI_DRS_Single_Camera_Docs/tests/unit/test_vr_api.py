"""
Unit tests for VR Pitch Teleportation REST API Endpoints
"""

from fastapi.testclient import TestClient
import pytest

from ai_drs.api.main import app

client = TestClient(app)


def test_vr_viewpoints_api():
    resp = client.get("/api/v1/vr/viewpoints")
    assert resp.status_code == 200
    data = resp.json()

    assert isinstance(data, list)
    assert len(data) >= 2
    assert any(v["viewpoint_id"] == "VR_FIRST_SLIP" for v in data)
