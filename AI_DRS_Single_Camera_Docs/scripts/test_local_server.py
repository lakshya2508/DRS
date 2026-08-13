"""
Local End-to-End Self-Testing Script for AI DRS Production Server
"""

import sys
import json
from pathlib import Path
from fastapi.testclient import TestClient

# Add src to Python search path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ai_drs.api.main import app

def run_local_system_verification():
    print("=" * 70)
    print(" RUNNING LOCAL END-TO-END PRODUCTION SYSTEM TEST")
    print("=" * 70)

    client = TestClient(app)
    headers = {"X-API-Key": "drs_live_prod_key_9981"}

    # 1. Main UI & Health Check
    res = client.get("/health")
    assert res.status_code == 200
    print(" [OK] 1. Root System Health Check passed (Status 200)")

    # 2. Minimum DRS API Health Check
    res = client.get("/api/v1/drs/health")
    assert res.status_code == 200
    print(f" [OK] 2. Minimal DRS API Health Check passed: {res.json()['status']}")

    # 3. Homography Pitch Calibration Endpoint
    calib_payload = {
        "image_points": [[294.4, 648.0], [985.6, 648.0], [704.0, 288.0], [576.0, 288.0]],
        "width": 1280,
        "height": 720
    }
    res = client.post("/api/v1/drs/calibrate", json=calib_payload)
    assert res.status_code == 200
    print(f" [OK] 3. Pitch Homography Calibration API passed (Reprojection Error: {res.json()['reprojection_error_px']}px)")

    # 4. UltraEdge Snicko Audio Endpoint
    snicko_payload = {
        "audio_amplitudes": [0.01] * 500,
        "sample_rate_hz": 44100
    }
    snicko_payload["audio_amplitudes"][250] = 0.95
    res = client.post("/api/v1/drs/snicko", json=snicko_payload)
    assert res.status_code == 200
    print(f" [OK] 4. UltraEdge Snicko Audio API passed (Spike Detected: {res.json()['spike_detected']})")

    # 5. Real Model Inference Status Endpoint
    res = client.get("/api/v1/model/status")
    assert res.status_code == 200
    print(f" [OK] 5. Model Inference Engine Status API passed (Backend: {res.json()['model_backend']})")

    # 6. Real Model Tensor Prediction Endpoint
    tensor_payload = {"width": 1280, "height": 720, "confidence_threshold": 0.35}
    res = client.post("/api/v1/model/predict_tensor", json=tensor_payload, headers=headers)
    assert res.status_code == 200
    print(f" [OK] 6. Real Model Tensor Prediction API passed ({len(res.json()['detections'])} detections found in {res.json()['inference_time_ms']}ms)")

    # 7. Local Open-Source LLM Chat Endpoint
    chat_payload = {"prompt": "What is the ICC rule for LBW impact?", "temperature": 0.3}
    res = client.post("/api/v1/llm/chat", json=chat_payload, headers=headers)
    assert res.status_code == 200
    print(f" [OK] 7. Open-Source Local LLM Chat API passed (Response length: {len(res.json()['response'])} chars)")

    print("=" * 70)
    print(" ALL LOCAL PRODUCTION SYSTEM ENDPOINTS ARE 100% OPERATIONAL!")
    print("=" * 70)

if __name__ == "__main__":
    run_local_system_verification()
