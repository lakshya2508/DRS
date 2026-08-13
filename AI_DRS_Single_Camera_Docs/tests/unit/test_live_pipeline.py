"""
Unit tests for Live Camera Processor & LBW Pipeline
"""

import numpy as np
import pytest
from fastapi.testclient import TestClient

from ai_drs.api.main import app
from ai_drs.pipeline.camera_processor import CameraFrame, CameraSource, LiveCameraProcessor
from ai_drs.pipeline.lbw_pipeline import (
    LiveLBWPipeline,
    classify_pitching,
    classify_impact,
    classify_wicket,
    icc_lbw_verdict,
    PITCH_GEOMETRY,
)

client = TestClient(app)


# ── Zone classification unit tests ─────────────────────────────────────────

def test_pitching_in_line():
    assert classify_pitching(640, 400, PITCH_GEOMETRY) == "IN_LINE"

def test_pitching_outside_off():
    assert classify_pitching(900, 400, PITCH_GEOMETRY) == "OUTSIDE_OFF"

def test_pitching_outside_leg():
    assert classify_pitching(300, 400, PITCH_GEOMETRY) == "OUTSIDE_LEG"


def test_impact_in_line():
    assert classify_impact(640, 490, PITCH_GEOMETRY) == "IN_LINE"

def test_impact_missing():
    assert classify_impact(900, 490, PITCH_GEOMETRY) == "MISSING"


def test_wicket_hitting():
    assert classify_wicket(640, PITCH_GEOMETRY) == "HITTING"

def test_wicket_missing():
    assert classify_wicket(900, PITCH_GEOMETRY) == "MISSING"


# ── ICC verdict logic ──────────────────────────────────────────────────────

def test_icc_verdict_out():
    verdict, conf = icc_lbw_verdict("IN_LINE", "IN_LINE", "HITTING")
    assert verdict == "OUT"
    assert conf > 90

def test_icc_verdict_not_out_outside_leg():
    verdict, _ = icc_lbw_verdict("OUTSIDE_LEG", "IN_LINE", "HITTING")
    assert verdict == "NOT_OUT"

def test_icc_verdict_not_out_outside_off():
    verdict, _ = icc_lbw_verdict("OUTSIDE_OFF", "IN_LINE", "HITTING")
    assert verdict == "NOT_OUT"

def test_icc_verdict_tracking():
    verdict, conf = icc_lbw_verdict("NOT_PITCHED_YET", "IN_LINE", "HITTING")
    assert verdict == "TRACKING"
    assert conf == 0.0

def test_icc_verdict_inconclusive():
    verdict, _ = icc_lbw_verdict("IN_LINE", "UMPIRES_CALL", "HITTING")
    assert verdict == "INCONCLUSIVE"


# ── LiveLBWPipeline ────────────────────────────────────────────────────────

def test_pipeline_processes_synthetic_frame():
    pipeline = LiveLBWPipeline()
    frame = np.zeros((720, 1280, 3), dtype=np.uint8)
    # Draw a red ball
    cv_present = True
    try:
        import cv2
        cv2.circle(frame, (640, 490), 14, (0, 0, 200), -1)
    except Exception:
        cv_present = False

    cam_frame = CameraFrame(frame=frame, frame_id=1, timestamp=1000.0, source="SYNTHETIC")
    decision = pipeline.process_frame(cam_frame)

    assert decision.verdict in ("OUT", "NOT_OUT", "INCONCLUSIVE", "TRACKING")
    assert decision.frame_id == 1
    assert decision.confidence_pct >= 0.0


# ── Camera processor ──────────────────────────────────────────────────────

def test_camera_processor_synthetic_start_stop():
    frames_seen = []
    def on_frame(f): frames_seen.append(f)

    proc = LiveCameraProcessor(
        source=CameraSource.SYNTHETIC,
        target_fps=30,
        on_frame=on_frame,
    )
    proc.start()
    import time; time.sleep(0.2)
    proc.stop()

    assert len(frames_seen) > 0
    assert frames_seen[0].width == 1280


# ── Pipeline REST API ──────────────────────────────────────────────────────

def test_pipeline_start_stop_api():
    res = client.post("/pipeline/start?source=SYNTHETIC&source_path=0")
    assert res.status_code == 200
    assert res.json()["status"] in ("started", "already_running")

    res = client.post("/pipeline/stop")
    assert res.status_code == 200
    assert res.json()["status"] == "stopped"


def test_pipeline_status_api():
    res = client.get("/pipeline/status")
    assert res.status_code == 200
    data = res.json()
    assert "running" in data


def test_live_dashboard_serves():
    res = client.get("/live")
    assert res.status_code == 200
    assert "AI DRS" in res.text
    assert "live_dashboard" in res.text or "LIVE MATCH" in res.text
