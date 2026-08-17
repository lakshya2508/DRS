"""
Unit tests for Asynchronous Processing Job Engine & Confidence Data Models.
"""

import time
import pytest
from fastapi.testclient import TestClient

from ai_drs.api.main import app
from ai_drs.models.confidence_models import ConfidenceMetric, IndependentDeliveryRecord
from ai_drs.jobs.job_manager import AsyncJobManager

client = TestClient(app)


def test_confidence_metric_status():
    m_high = ConfidenceMetric.create(140.0, "km/h", 0.95)
    assert m_high.status == "high"
    assert m_high.value == 140.0

    m_est = ConfidenceMetric.create(135.0, "km/h", 0.70)
    assert m_est.status == "estimated"

    m_unc = ConfidenceMetric.create(120.0, "km/h", 0.40)
    assert m_unc.status == "uncertain"


def test_async_job_manager_flow():
    mgr = AsyncJobManager()
    job = mgr.create_job("C:/Users/Hello-pc/Downloads/archive (1)/Dataset/train/LBW/lbw1.mp4")
    assert job.status in ["queued", "extracting_frames", "detecting_ball"]
    assert job.job_id.startswith("job_")

    # Poll until completed
    for _ in range(10):
        time.sleep(0.3)
        st = mgr.get_job(job.job_id)
        if st and st.status == "completed":
            break

    final_st = mgr.get_job(job.job_id)
    assert final_st is not None
    assert final_st.progress_pct == 100


def test_job_api_create_and_status():
    res = client.post("/api/v1/jobs/create", json={"video_path": "sample.mp4"})
    assert res.status_code == 200
    data = res.json()
    assert "job_id" in data
    assert data["status"] in ["queued", "extracting_frames"]

    job_id = data["job_id"]
    res2 = client.get(f"/api/v1/jobs/{job_id}/status")
    assert res2.status_code == 200
    assert res2.json()["job_id"] == job_id


def test_independent_delivery_endpoint():
    res = client.get("/api/v1/jobs/delivery/del_7788")
    assert res.status_code == 200
    data = res.json()
    assert data["delivery_id"] == "del_7788"
    assert data["speed"]["value"] == 142.8
    assert data["speed"]["confidence"] == 0.94
    assert data["speed"]["status"] == "high"
