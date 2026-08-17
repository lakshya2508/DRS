"""
Unit tests for Real Model Weight Loading & Tensor Inference API Endpoints
"""

import numpy as np
import pytest
from fastapi.testclient import TestClient

from ai_drs.api.main import app
from ai_drs.detection.real_model_inference import (
    ModelPredictionResult,
    RealModelInferenceEngine,
)

client = TestClient(app)


def test_real_model_inference_engine_prediction():
    engine = RealModelInferenceEngine()
    img = np.zeros((720, 1280, 3), dtype=np.uint8)

    result = engine.predict_image(img, confidence_threshold=0.30, is_synthetic=True)

    assert isinstance(result, ModelPredictionResult)
    assert result.image_width == 1280
    assert result.image_height == 720
    assert len(result.detections) > 0
    assert result.inference_time_ms >= 0.0


def test_model_status_api_endpoint():
    response = client.get("/api/v1/model/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ("ACTIVE", "UNINITIALIZED")
    assert "weights_path" in data
    assert "model_backend" in data


def test_model_load_weights_api_endpoint(tmp_path):
    weights_file = tmp_path / "custom_weights.pt"
    weights_file.write_bytes(b"TEST_WEIGHTS_DATA")

    payload = {"weights_path": str(weights_file)}
    headers = {"X-API-Key": "drs_live_prod_key_9981"}
    response = client.post("/api/v1/model/load", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "SUCCESS"
    assert data["weights_path"] == str(weights_file)


def test_model_predict_tensor_api_endpoint():
    payload = {"width": 1280, "height": 720, "confidence_threshold": 0.35}
    headers = {"X-API-Key": "drs_live_prod_key_9981"}
    response = client.post("/api/v1/model/predict_tensor", json=payload, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "detections" in data
    assert len(data["detections"]) > 0
    assert data["image_width"] == 1280
