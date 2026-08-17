"""
Live LBW Decision Pipeline — Processes every camera frame through ball detection,
tracking, pitch zone analysis and ICC LBW decision logic in real-time.
"""

import time
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

import cv2
import numpy as np

from ai_drs.common.logging import setup_logger
from ai_drs.detection.real_model_inference import RealModelInferenceEngine
from ai_drs.pipeline.camera_processor import CameraFrame

logger = setup_logger("ai_drs.pipeline.lbw_pipeline")


# --------------------------------------------------------------------------
# Data structures
# --------------------------------------------------------------------------

@dataclass
class BallPosition:
    frame_id:  int
    x:         float
    y:         float
    confidence: float
    timestamp: float


@dataclass
class LiveLBWDecision:
    decision_id:    str
    frame_id:       int
    timestamp:      float
    verdict:        str          # OUT / NOT_OUT / INCONCLUSIVE / TRACKING
    pitching_zone:  str          # IN_LINE / OUTSIDE_OFF / OUTSIDE_LEG / NOT_PITCHED_YET
    impact_zone:    str          # IN_LINE / UMPIRES_CALL / MISSING / NOT_REACHED_YET
    wicket_zone:    str          # HITTING / UMPIRES_CALL / MISSING / NOT_APPLICABLE
    confidence_pct: float
    ball_speed_kmh: float
    trajectory:     List[Tuple[float, float]] = field(default_factory=list)
    voice_callout:  str          = ""
    annotated_frame: Optional[np.ndarray] = None


# --------------------------------------------------------------------------
# Pitch zone geometry (normalised to 1280×720 frame)
# --------------------------------------------------------------------------

PITCH_GEOMETRY = {
    "stump_left_x":   608.0,
    "stump_right_x":  672.0,
    "crease_y":       520.0,     # batter's crease
    "popping_y":      280.0,     # bowler end crease
    "wicket_top_y":   445.0,
    "wicket_bottom_y": 520.0,
}


def classify_pitching(bx: float, by: float, pg: dict) -> str:
    if by < pg["popping_y"] or by > pg["crease_y"]:
        return "NOT_PITCHED_YET"
    if pg["stump_left_x"] - 30 <= bx <= pg["stump_right_x"] + 30:
        return "IN_LINE"
    if bx < pg["stump_left_x"] - 30:
        return "OUTSIDE_LEG"
    return "OUTSIDE_OFF"


def classify_impact(bx: float, by: float, pg: dict) -> str:
    if by < pg["wicket_top_y"]:
        return "NOT_REACHED_YET"
    if pg["stump_left_x"] <= bx <= pg["stump_right_x"]:
        return "IN_LINE"
    margin = 20.0
    if pg["stump_left_x"] - margin <= bx <= pg["stump_right_x"] + margin:
        return "UMPIRES_CALL"
    return "MISSING"


def classify_wicket(bx: float, pg: dict) -> str:
    if pg["stump_left_x"] - 5 <= bx <= pg["stump_right_x"] + 5:
        return "HITTING"
    margin = 18.0
    if pg["stump_left_x"] - margin <= bx <= pg["stump_right_x"] + margin:
        return "UMPIRES_CALL"
    return "MISSING"


def icc_lbw_verdict(pitching: str, impact: str, wicket: str) -> Tuple[str, float]:
    """Apply ICC LBW 3-zone rule and return (verdict, confidence_pct)."""
    if pitching == "OUTSIDE_LEG":
        return "NOT_OUT", 96.0
    if pitching == "OUTSIDE_OFF":
        return "NOT_OUT", 91.0
    if pitching == "NOT_PITCHED_YET":
        return "TRACKING", 0.0
    if impact == "NOT_REACHED_YET":
        return "TRACKING", 0.0
    if impact == "MISSING":
        return "NOT_OUT", 88.0
    if wicket == "MISSING":
        return "NOT_OUT", 85.0
    if impact == "IN_LINE" and wicket == "HITTING":
        return "OUT", 94.0
    if impact == "UMPIRES_CALL" or wicket == "UMPIRES_CALL":
        return "INCONCLUSIVE", 62.0
    return "NOT_OUT", 78.0


# --------------------------------------------------------------------------
# Pipeline
# --------------------------------------------------------------------------

class LiveLBWPipeline:
    """
    Real-time LBW decision pipeline.
    Processes CameraFrame objects → produces LiveLBWDecision every frame.
    """

    def __init__(self, model_weights_path: Optional[str] = None):
        self.model        = RealModelInferenceEngine(weights_path=model_weights_path)
        self.trajectory:  List[BallPosition] = []
        self.last_decision: Optional[LiveLBWDecision] = None
        self._delivery_active = False
        self._frame_count = 0
        logger.info("LiveLBWPipeline initialised.")

    # ------------------------------------------------------------------
    # Main entry: process one frame
    # ------------------------------------------------------------------

    def process_frame(self, cam_frame: CameraFrame) -> LiveLBWDecision:
        self._frame_count += 1
        img = cam_frame.frame.copy()

        # 1. Detect ball (strictly capture ONLY cricket balls)
        is_synth = getattr(cam_frame, "source_type", "") == "SYNTHETIC" or getattr(cam_frame, "source_path", "") == "synthetic"
        result = self.model.predict_image(img, confidence_threshold=0.30, is_synthetic=is_synth)
        ball_detections = [d for d in result.detections if d.class_label == "cricket_ball"]

        if ball_detections:
            best = max(ball_detections, key=lambda d: d.confidence)
            pos  = BallPosition(
                frame_id   = cam_frame.frame_id,
                x          = best.center_x,
                y          = best.center_y,
                confidence = best.confidence,
                timestamp  = cam_frame.timestamp,
            )
            self.trajectory.append(pos)
            if len(self.trajectory) > 90:          # keep last 3 seconds at 30fps
                self.trajectory = self.trajectory[-90:]
            self._delivery_active = True
        else:
            pos = None

        # 2. Compute ball speed (pixels/sec → km/h approximation)
        speed_kmh = self._estimate_speed()

        # 3. Zone classification
        if pos:
            pitching = classify_pitching(pos.x, pos.y, PITCH_GEOMETRY)
            impact   = classify_impact(pos.x, pos.y, PITCH_GEOMETRY)
            wicket   = classify_wicket(pos.x, PITCH_GEOMETRY)
        else:
            pitching = "NOT_PITCHED_YET"
            impact   = "NOT_REACHED_YET"
            wicket   = "NOT_APPLICABLE"

        # 4. LBW verdict
        verdict, conf = icc_lbw_verdict(pitching, impact, wicket)

        # 5. Voice callout
        voice = self._build_voice_callout(verdict, pitching, impact, wicket, conf)

        # 6. Annotate frame
        annotated = self._annotate_frame(img, pos, verdict, conf, pitching, impact, wicket, speed_kmh)

        decision = LiveLBWDecision(
            decision_id    = str(uuid.uuid4())[:8].upper(),
            frame_id       = cam_frame.frame_id,
            timestamp      = cam_frame.timestamp,
            verdict        = verdict,
            pitching_zone  = pitching,
            impact_zone    = impact,
            wicket_zone    = wicket,
            confidence_pct = round(conf, 1),
            ball_speed_kmh = round(speed_kmh, 1),
            trajectory     = [(p.x, p.y) for p in self.trajectory[-20:]],
            voice_callout  = voice,
            annotated_frame= annotated,
        )
        self.last_decision = decision
        return decision

    def reset_delivery(self):
        """Call between deliveries to clear trajectory buffer."""
        self.trajectory.clear()
        self._delivery_active = False
        logger.info("Delivery reset — trajectory cleared.")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _estimate_speed(self) -> float:
        if len(self.trajectory) < 2:
            return 0.0
        p1, p2 = self.trajectory[-2], self.trajectory[-1]
        dt = max(p2.timestamp - p1.timestamp, 1e-6)
        pixel_dist = np.hypot(p2.x - p1.x, p2.y - p1.y)
        # Rough calibration: 1 pixel ≈ 0.01 m at 20m distance
        metres_per_sec = (pixel_dist * 0.01) / dt
        return metres_per_sec * 3.6

    def _build_voice_callout(self, verdict, pitching, impact, wicket, conf) -> str:
        if verdict == "TRACKING":
            return "Ball in flight... tracking."
        if verdict == "OUT":
            return f"OUT! LBW! Pitched {pitching.replace('_',' ')}, impact {impact.replace('_',' ')}, hitting stumps. Confidence {conf:.0f}%."
        if verdict == "NOT_OUT":
            if pitching in ("OUTSIDE_OFF", "OUTSIDE_LEG"):
                return f"NOT OUT — pitched {pitching.replace('_',' ')}."
            return f"NOT OUT — ball missing stumps. Confidence {conf:.0f}%."
        return f"INCONCLUSIVE — Umpire's Call. Confidence {conf:.0f}%."

    def _annotate_frame(self, img, pos, verdict, conf, pitching, impact, wicket, speed) -> np.ndarray:
        h, w = img.shape[:2]

        # --- Trajectory trail ---
        pts = [(int(p.x), int(p.y)) for p in self.trajectory[-20:]]
        for i in range(1, len(pts)):
            alpha = i / len(pts)
            color = (0, int(255 * alpha), int(255 * (1 - alpha)))
            cv2.line(img, pts[i-1], pts[i], color, 2)

        # --- Ball circle ---
        if pos:
            bx, by = int(pos.x), int(pos.y)
            cv2.circle(img, (bx, by), 16, (0, 255, 255), 2)
            cv2.circle(img, (bx, by), 4,  (0, 255, 255), -1)

        # --- Two-Wicket Pitch Scanner Overlay ---
        # Wicket A (Striker's End) — Bottom of pitch
        wa_cx, wa_cy = 960, 920
        # Wicket B (Bowler's End) — Top of pitch
        wb_cx, wb_cy = 960, 240

        # Scale coordinates relative to frame dimensions (w, h)
        wa_x = int(wa_cx * (w / 1920.0))
        wa_y = int(wa_cy * (h / 1080.0))
        wb_x = int(wb_cx * (w / 1920.0))
        wb_y = int(wb_cy * (h / 1080.0))

        # 1. Primary Pitch Axis Centerline (Yellow line connecting Wicket B to Wicket A)
        cv2.line(img, (wb_x, wb_y), (wa_x, wa_y), (0, 255, 255), 2, cv2.LINE_AA)
        cv2.circle(img, (wa_x, wa_y), 6, (0, 229, 160), -1) # Wicket A Center Dot
        cv2.circle(img, (wb_x, wb_y), 6, (0, 229, 160), -1) # Wicket B Center Dot

        # 2. Draw Wicket A (Striker's End 3 Stumps + Bails)
        stump_w = int(24 * (w / 1920.0))
        stump_h = int(65 * (h / 1080.0))
        for off in [-stump_w, 0, stump_w]:
            cv2.line(img, (wa_x + off, wa_y), (wa_x + off, wa_y - stump_h), (0, 255, 255), 3)
        cv2.line(img, (wa_x - stump_w - 4, wa_y - stump_h), (wa_x + stump_w + 4, wa_y - stump_h), (0, 229, 160), 2)
        cv2.putText(img, "WICKET A (Striker)", (wa_x - 70, wa_y + 22), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 229, 160), 1)

        # 3. Draw Wicket B (Bowler's End 3 Stumps + Bails)
        sb_w = int(14 * (w / 1920.0))
        sb_h = int(35 * (h / 1080.0))
        for off in [-sb_w, 0, sb_w]:
            cv2.line(img, (wb_x + off, wb_y), (wb_x + off, wb_y - sb_h), (0, 255, 255), 2)
        cv2.line(img, (wb_x - sb_w - 2, wb_y - sb_h), (wb_x + sb_w + 2, wb_y - sb_h), (0, 229, 160), 2)
        cv2.putText(img, "WICKET B (Bowler)", (wb_x - 65, wb_y - sb_h - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.42, (0, 229, 160), 1)

        # 4. Popping Crease Lines
        crease_wa_w = int(180 * (w / 1920.0))
        crease_wb_w = int(90 * (w / 1920.0))
        cv2.line(img, (wa_x - crease_wa_w, wa_y - 25), (wa_x + crease_wa_w, wa_y - 25), (255, 255, 0), 1)
        cv2.line(img, (wb_x - crease_wb_w, wb_y + 15), (wb_x + crease_wb_w, wb_y + 15), (255, 255, 0), 1)

        # --- Top HUD bar ---
        cv2.rectangle(img, (0, 0), (w, 52), (0, 0, 0), -1)

        # Verdict colour
        v_color = {"OUT": (0,50,255), "NOT_OUT": (0,200,0),
                   "INCONCLUSIVE": (0,165,255), "TRACKING": (180,180,180)}.get(verdict, (255,255,255))
        cv2.rectangle(img, (0, 0), (220, 52), v_color, -1)
        cv2.putText(img, verdict, (8, 36), cv2.FONT_HERSHEY_DUPLEX, 1.0, (255,255,255), 2)

        cv2.putText(img, f"Conf: {conf:.0f}%  |  Speed: {speed:.0f} km/h",
                    (230, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200,200,200), 1)
        cv2.putText(img, f"Pitch: {pitching}  Impact: {impact}  Wicket: {wicket}",
                    (230, 42), cv2.FONT_HERSHEY_SIMPLEX, 0.48, (180,240,180), 1)

        # Two-Wicket Scanner Badge (Top Right)
        cv2.rectangle(img, (w - 280, 8), (w - 10, 44), (20, 40, 30), -1)
        cv2.rectangle(img, (w - 280, 8), (w - 10, 44), (0, 229, 160), 1)
        cv2.putText(img, "2-WICKET SCANNER: LOCKED", (w - 270, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 229, 160), 1)

        return img
