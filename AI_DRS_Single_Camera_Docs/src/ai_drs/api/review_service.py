"""
End-to-End Review Pipeline Service for AI DRS
"""

import uuid
from pathlib import Path
from typing import Any, Dict, Optional, Union
from pydantic import BaseModel, Field

from ai_drs.calibration.pitch_calibration import CalibrationData, PitchCalibrator, Point2D
from ai_drs.common.logging import setup_logger
from ai_drs.decision.lbw_engine import LBWDecisionEngine
from ai_drs.detection.ball_detector import ClassicalBallDetector
from ai_drs.detection.stump_detector import StumpDetector
from ai_drs.events.event_detector import EventDetector
from ai_drs.ingestion.video_ingestion import VideoIngestor
from ai_drs.tracking.ball_tracker import KalmanBallTracker
from ai_drs.trajectory.trajectory_engine import TrajectoryEngine

logger = setup_logger("ai_drs.service")


class ReviewResultResponse(BaseModel):
    """Schema representing end-to-end review output payload (TRD Section 15)."""
    review_id: str
    result: str = Field(description="'OUT', 'NOT_OUT', or 'INCONCLUSIVE'")
    confidence: float
    recommendation_reason: str
    pitching: Dict[str, Any]
    impact: Dict[str, Any]
    wicket: Dict[str, Any]
    ball_track: Dict[str, Any]
    calibration: Dict[str, Any]
    pipeline_version: str = Field(default="0.9.0")

    @property
    def decision(self) -> str:
        return self.result

    @property
    def confidence_score(self) -> float:
        return self.confidence




class ReviewPipelineService:
    """Orchestrates end-to-end execution of all AI DRS computer vision & decision modules."""

    def __init__(self):
        self.ingestor = VideoIngestor()
        self.ball_detector = ClassicalBallDetector()
        self.ball_tracker = KalmanBallTracker()
        self.stump_detector = StumpDetector()
        self.event_detector = EventDetector()
        self.trajectory_engine = TrajectoryEngine()
        self.decision_engine = LBWDecisionEngine()

    def create_default_calibration(self, width: int = 1280, height: int = 720) -> CalibrationData:
        """Creates default synthetic calibration if none provided."""
        pitch_pts = [
            Point2D(x=-1.32, y=1.22),
            Point2D(x=1.32, y=1.22),
            Point2D(x=1.32, y=20.12),
            Point2D(x=-1.32, y=20.12),
        ]
        image_pts = [
            Point2D(x=width * 0.23, y=height * 0.90),
            Point2D(x=width * 0.77, y=height * 0.90),
            Point2D(x=width * 0.55, y=height * 0.40),
            Point2D(x=width * 0.45, y=height * 0.40),
        ]
        calibrator = PitchCalibrator()
        return calibrator.calibrate(image_pts, pitch_pts, image_size=(width, height), camera_id="default_synthetic")

    def process_review(
        self,
        video_path: Union[str, Path],
        calibration: Optional[CalibrationData] = None,
        batter_stance: str = "RHB"
    ) -> ReviewResultResponse:
        """Alias for process_video."""
        return self.process_video(video_path, calibration=calibration, batter_stance=batter_stance)

    def process_video(
        self,
        video_path: Union[str, Path],
        calibration: Optional[CalibrationData] = None,
        batter_stance: str = "RHB"
    ) -> ReviewResultResponse:

        """Runs the complete E2E AI DRS pipeline on a delivery video."""
        review_id = f"REV-{uuid.uuid4().hex[:8].upper()}"
        path = Path(video_path).resolve()
        logger.info(f"Starting E2E AI DRS review [{review_id}] for video: {path.name}")

        # Step 1: Ingestion
        meta = self.ingestor.extract_metadata(path)
        if not meta.is_valid:
            logger.warning(f"Review [{review_id}] video ingestion failed: {meta.validation_error}")
            return self._build_inconclusive_response(review_id, f"Video ingestion failed: {meta.validation_error}")

        frames = list(self.ingestor.stream_frames(path))
        if not frames:
            return self._build_inconclusive_response(review_id, "No frames could be extracted from video.")

        # Step 2: Calibration
        calib = calibration or self.create_default_calibration(width=meta.width, height=meta.height)

        # Step 3: Stump & Wicket Geometry
        first_frame_img = frames[0].image
        wicket_geo = self.stump_detector.detect_stumps(first_frame_img, calibration=calib)

        # Step 4: Ball Detection per frame
        frame_detections = []
        prev_img = None
        for frame in frames:
            dets = self.ball_detector.detect(frame.image, frame_id=frame.frame_index, prev_image=prev_img)
            frame_detections.append((frame.frame_index, dets))
            prev_img = frame.image

        # Step 5: Ball Tracking
        track = self.ball_tracker.track_sequence(frame_detections, track_id=f"track_{review_id}")

        # Step 6: Event Detection (Pitching & Impact)
        pitching = self.event_detector.detect_pitching(track, calibration=calib, batter_stance=batter_stance) if track else None
        impact = self.event_detector.detect_impact(track, calibration=calib, batter_stance=batter_stance) if track else None

        # Step 7: Trajectory Extrapolation & Wicket Projection
        trajectory = self.trajectory_engine.predict_trajectory(track, pitching, impact, calib) if track else None

        # Step 8: LBW Decision Engine
        lbw_decision = self.decision_engine.evaluate(
            pitching_event=pitching,
            impact_event=impact,
            trajectory_prediction=trajectory,
            ball_track=track,
            calibration=calib,
            shot_offered=True
        )

        logger.info(f"Completed review [{review_id}]: Result={lbw_decision.result}, Conf={lbw_decision.confidence:.2f}")

        # Step 9: Assemble TRD Section 15 Payload
        return ReviewResultResponse(
            review_id=review_id,
            result=lbw_decision.result,
            confidence=lbw_decision.confidence,
            recommendation_reason=lbw_decision.recommendation_reason,
            pitching={
                "zone": pitching.zone if pitching else "UNKNOWN",
                "confidence": pitching.confidence if pitching else 0.0,
                "frame_id": pitching.frame_id if pitching else -1,
                "metric_x": pitching.metric_point.x if pitching else 0.0,
                "metric_y": pitching.metric_point.y if pitching else 0.0,
            },
            impact={
                "zone": impact.zone if impact else "UNKNOWN",
                "confidence": impact.confidence if impact else 0.0,
                "frame_id": impact.frame_id if impact else -1,
                "metric_x": impact.metric_point.x if impact else 0.0,
                "metric_y": impact.metric_point.y if impact else 0.0,
            },
            wicket={
                "hit_result": trajectory.wicket_projection.hit_result if trajectory else "UNKNOWN",
                "hit_probability": trajectory.wicket_projection.hit_probability if trajectory else 0.0,
                "projected_x_m": trajectory.wicket_projection.projected_x_m if trajectory else 0.0,
                "projected_z_m": trajectory.wicket_projection.projected_z_m if trajectory else 0.0,
                "confidence": trajectory.wicket_projection.confidence if trajectory else 0.0,
            },
            ball_track={
                "total_frames": track.total_frames if track else 0,
                "coverage_ratio": track.coverage_ratio if track else 0.0,
                "track_confidence": track.track_confidence if track else 0.0,
            },
            calibration={
                "reprojection_error_px": calib.reprojection_error_px,
                "is_valid": calib.is_valid,
            },
            pipeline_version="0.9.0"
        )

    def _build_inconclusive_response(self, review_id: str, reason: str) -> ReviewResultResponse:
        return ReviewResultResponse(
            review_id=review_id,
            result="INCONCLUSIVE",
            confidence=0.0,
            recommendation_reason=f"INCONCLUSIVE: {reason}",
            pitching={"zone": "UNKNOWN", "confidence": 0.0},
            impact={"zone": "UNKNOWN", "confidence": 0.0},
            wicket={"hit_result": "UNKNOWN", "hit_probability": 0.0, "confidence": 0.0},
            ball_track={"coverage_ratio": 0.0},
            calibration={"reprojection_error_px": 999.0, "is_valid": False},
            pipeline_version="0.9.0"
        )
