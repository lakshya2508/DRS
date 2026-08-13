"""
Unit tests for Webhook & Cloud Backup REST API Endpoints
"""

from fastapi.testclient import TestClient
import pytest

from ai_drs.api.main import app

client = TestClient(app)


def test_register_webhook_api():
    resp = client.post("/api/v1/enterprise/webhooks/register", json={"webhook_url": "https://client.com/drs-hook"})
    assert resp.status_code == 200
    data = resp.json()

    assert data["status"] == "REGISTERED"
    assert data["webhook_url"] == "https://client.com/drs-hook"


def test_trigger_cloud_backup_api():
    resp = client.post("/api/v1/enterprise/backup/M_API_BACKUP_01?asset_name=summary.pdf")
    assert resp.status_code == 200
    data = resp.json()

    assert data["match_id"] == "M_API_BACKUP_01"
    assert data["is_backup_successful"] is True
