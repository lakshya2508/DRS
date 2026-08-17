"""
Unit tests for Dataset Delivery Classifier and API endpoints.
"""

from pathlib import Path
import pytest
from fastapi.testclient import TestClient

from ai_drs.api.main import app
from ai_drs.detection.dataset_classifier import DatasetDeliveryClassifier

client = TestClient(app)


def test_list_dataset_clips():
    classifier = DatasetDeliveryClassifier()
    clips = classifier.list_available_clips()
    assert isinstance(clips, dict)
    assert "LBW" in clips
    assert "Legal" in clips
    assert len(clips["LBW"]) > 0


def test_classify_real_lbw_clip():
    classifier = DatasetDeliveryClassifier()
    clips = classifier.list_available_clips()
    assert len(clips["LBW"]) > 0
    sample_clip = clips["LBW"][0]

    res = classifier.classify_video_file(sample_clip)
    assert res.predicted_class == "LBW"
    assert res.drs_decision == "OUT"
    assert res.confidence_pct > 80.0
    assert res.detected_frames > 0


def test_api_dataset_clips():
    res = client.get("/api/v1/dataset/clips")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["total_clips"] > 0
    assert "LBW" in data["clips"]


def test_api_dataset_classify_clip():
    classifier = DatasetDeliveryClassifier()
    clips = classifier.list_available_clips()
    sample_clip = clips["LBW"][0]

    res = client.post("/api/v1/dataset/classify", params={"video_path": sample_clip})
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "ok"
    assert data["result"]["predicted_class"] == "LBW"
