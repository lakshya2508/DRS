"""
Unit tests for Minimum AI DRS Production API Endpoints
"""

import pytest
from fastapi.testclient import TestClient

from ai_drs.api.main import app

client = TestClient(app)


def test_minimal_drs_health():
    response = client.get("/api/v1/drs/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ONLINE"
    assert "AI DRS Minimum" in data["system"]


def test_minimal_drs_calibrate_endpoint():
    payload = {
        "image_points": [[294.4, 648.0], [985.6, 648.0], [704.0, 288.0], [576.0, 288.0]],
        "width": 1280,
        "height": 720
    }
    response = client.post("/api/v1/drs/calibrate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] is True
    assert "camera_id" in data


def test_minimal_drs_snicko_endpoint():
    audio_samples = [0.01] * 500
    audio_samples[250] = 0.95
    payload = {
        "audio_amplitudes": audio_samples,
        "sample_rate_hz": 44100
    }
    response = client.post("/api/v1/drs/snicko", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "spike_detected" in data
    assert "confidence_pct" in data
