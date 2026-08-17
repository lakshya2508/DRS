"""
Unit tests for Hardware Discovery and Match Report Router endpoints.
"""

import pytest
from fastapi.testclient import TestClient

from ai_drs.api.main import app

client = TestClient(app)


def test_hardware_devices_endpoint():
    res = client.get("/api/v1/hardware/devices")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert "opencv_version" in data
    assert "detected_cameras" in data


def test_report_generate_html_endpoint():
    res = client.get("/api/v1/reports/generate/MATCH_TEST_101")
    assert res.status_code == 200
    assert "<!DOCTYPE html>" in res.text
    assert "AI DRS Match Report" in res.text
