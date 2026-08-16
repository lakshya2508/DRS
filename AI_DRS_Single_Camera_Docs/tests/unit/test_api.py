"""
Unit tests for FastAPI REST API endpoints
"""

import io
import tempfile
from pathlib import Path
from fastapi.testclient import TestClient
import pytest

from ai_drs.api.main import app
from ai_drs.calibration.pitch_calibration import CalibrationData, Point2D
from ai_drs.ingestion.video_ingestion import create_synthetic_video

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "<!DOCTYPE html>" in response.text
    assert "ai" in response.text.lower() or "cricket" in response.text.lower()


def test_read_health():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["version"] == "2.0.0"



def test_create_calibration_endpoint():
    payload = {
        "camera_id": "test_cam_1",
        "image_width": 1280,
        "image_height": 720,
        "image_points": [{"x": 300, "y": 900}, {"x": 980, "y": 900}, {"x": 700, "y": 300}, {"x": 580, "y": 300}],
        "pitch_points": [{"x": -1.32, "y": 1.22}, {"x": 1.32, "y": 1.22}, {"x": 1.32, "y": 20.12}, {"x": -1.32, "y": 20.12}],
        "homography_matrix": [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]],
        "inv_homography_matrix": [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]],
        "reprojection_error_px": 0.5,
        "is_valid": True
    }

    response = client.post("/api/v1/calibration", json=payload)
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "success"
    assert data["camera_id"] == "test_cam_1"


def test_create_review_unsupported_file():
    files = {"file": ("test.txt", b"dummy content", "text/plain")}
    response = client.post("/api/v1/reviews", files=files)
    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]


def test_create_and_get_review_pipeline():
    with tempfile.TemporaryDirectory() as tmpdir:
        video_path = Path(tmpdir) / "test_delivery_upload.mp4"
        create_synthetic_video(video_path, num_frames=15, width=1280, height=720, fps=30.0)

        with open(video_path, "rb") as f:
            files = {"file": ("test_delivery_upload.mp4", f, "video/mp4")}
            response = client.post("/api/v1/reviews?batter_stance=RHB", files=files)

        assert response.status_code == 201
        data = response.json()
        assert "review_id" in data
        assert data["result"] in ("OUT", "NOT_OUT", "INCONCLUSIVE")
        assert "pipeline_version" in data

        review_id = data["review_id"]

        # Fetch review by ID
        get_res = client.get(f"/api/v1/reviews/{review_id}")
        assert get_res.status_code == 200
        assert get_res.json()["review_id"] == review_id

        # Fetch review evidence
        ev_res = client.get(f"/api/v1/reviews/{review_id}/evidence")
        assert ev_res.status_code == 200
        ev_data = ev_res.json()
        assert "evidence" in ev_data
        assert "pitching" in ev_data["evidence"]
        assert "impact" in ev_data["evidence"]


def test_get_nonexistent_review():
    response = client.get("/api/v1/reviews/NON_EXISTENT_ID")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]


def test_match_engine_api_e2e():
    # 1. Create match
    create_payload = {
        "match_id": "M_API_101",
        "team_a": "India",
        "team_b": "Australia",
        "striker_name": "V. Kohli",
        "non_striker_name": "R. Sharma",
        "bowler_name": "M. Starc",
        "total_overs": 20,
        "target": 160
    }
    res_create = client.post("/api/v1/match/create", json=create_payload)
    assert res_create.status_code == 201
    assert res_create.json()["match_id"] == "M_API_101"

    # 2. Conduct toss
    toss_payload = {
        "caller_team": "India",
        "caller_call": "HEADS",
        "winner_decision": "BAT"
    }
    res_toss = client.post("/api/v1/match/M_API_101/toss", json=toss_payload)
    assert res_toss.status_code == 200
    assert "toss" in res_toss.json()

    # 3. Process delivery
    delivery_payload = {
        "delivery_id": "D1",
        "over_number": 0,
        "ball_number_in_over": 1,
        "striker_name": "V. Kohli",
        "non_striker_name": "R. Sharma",
        "bowler_name": "M. Starc",
        "runs_off_bat": 4
    }
    res_deliv = client.post("/api/v1/match/M_API_101/delivery", json=delivery_payload)
    assert res_deliv.status_code == 200
    deliv_data = res_deliv.json()
    assert deliv_data["match_state"]["score"] == 4

    # 4. Fetch Scoreboard
    res_score = client.get("/api/v1/match/M_API_101/scoreboard")
    assert res_score.status_code == 200
    assert res_score.json()["score"] == 4

    # 5. Fetch Live Cards
    res_cards = client.get("/api/v1/match/M_API_101/cards")
    assert res_cards.status_code == 200
    assert "V. Kohli" in res_cards.json()["striker_card"]["formatted_string"]

    # 6. Fetch Condition Panel
    res_cond = client.get("/api/v1/match/M_API_101/condition-panel")
    assert res_cond.status_code == 200
    assert res_cond.json()["runs_required"] == 156

    # 7. Fetch Analytics
    res_analytics = client.get("/api/v1/match/M_API_101/analytics")
    assert res_analytics.status_code == 200
    assert res_analytics.json()["match_id"] == "M_API_101"

