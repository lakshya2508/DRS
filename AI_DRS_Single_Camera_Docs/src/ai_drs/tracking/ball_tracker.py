"""
Ball Tracking Engine for AI DRS (2D Kalman Filter & Data Association)
"""

from typing import List, Optional, Tuple
import cv2
import numpy as np
from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger
from ai_drs.detection.ball_detector import BallDetection

logger = setup_logger("ai_drs.tracking")


class TrackedPoint(BaseModel):
    """Represents a single frame point in a smoothed ball track."""
    frame_id: int = Field(ge=0)
    x: float = Field(description="Center X coordinate in pixels")
    y: float = Field(description="Center Y coordinate in pixels")
    vx: float = Field(default=0.0, description="Estimated X velocity (px/frame)")
    vy: float = Field(default=0.0, description="Estimated Y velocity (px/frame)")
    confidence: float = Field(ge=0.0, le=1.0)
    is_interpolated: bool = Field(default=False, description="True if predicted/interpolated during occlusion")


class BallTrack(BaseModel):
    """Pydantic model representing a complete delivery ball track."""
    track_id: str = Field(default="track_0")
    points: List[TrackedPoint] = Field(default_factory=list)
    start_frame: int = Field(default=0)
    end_frame: int = Field(default=0)
    total_frames: int = Field(default=0)
    detected_count: int = Field(default=0)
    interpolated_count: int = Field(default=0)
    coverage_ratio: float = Field(default=0.0, ge=0.0, le=1.0)
    track_confidence: float = Field(default=0.0, ge=0.0, le=1.0)


class KalmanBallTracker:
    """Kalman Filter-backed single-object ball tracker for delivery sequences."""

    def __init__(
        self,
        gating_threshold_px: float = 80.0,
        max_missed_frames: int = 5,
        min_track_length: int = 4
    ):
        self.gating_threshold_px = gating_threshold_px
        self.max_missed_frames = max_missed_frames
        self.min_track_length = min_track_length

        self.kalman: Optional[cv2.KalmanFilter] = None
        self.tracked_points: List[TrackedPoint] = []
        self.missed_frames_count = 0
        self.is_active = False

    def _init_kalman(self, initial_x: float, initial_y: float) -> cv2.KalmanFilter:
        """Initializes 2D Constant-Velocity Kalman Filter [x, y, vx, vy]."""
        kf = cv2.KalmanFilter(4, 2)
        # Transition matrix F
        kf.transitionMatrix = np.array(
            [[1.0, 0.0, 1.0, 0.0],
             [0.0, 1.0, 0.0, 1.0],
             [0.0, 0.0, 1.0, 0.0],
             [0.0, 0.0, 0.0, 1.0]],
            dtype=np.float32
        )
        # Measurement matrix H
        kf.measurementMatrix = np.array(
            [[1.0, 0.0, 0.0, 0.0],
             [0.0, 1.0, 0.0, 0.0]],
            dtype=np.float32
        )
        # Process noise covariance Q
        kf.processNoiseCov = np.eye(4, dtype=np.float32) * 1e-2
        # Measurement noise covariance R
        kf.measurementNoiseCov = np.eye(2, dtype=np.float32) * 1e-1
        # Posteriori error covariance P
        kf.errorCovPost = np.eye(4, dtype=np.float32) * 1.0

        # Initial state
        kf.statePost = np.array([[initial_x], [initial_y], [0.0], [0.0]], dtype=np.float32)
        return kf

    def track_sequence(
        self,
        frame_detections: List[Tuple[int, List[BallDetection]]],
        track_id: str = "track_0"
    ) -> Optional[BallTrack]:
        """Tracks ball across a sequence of per-frame detections."""
        self.tracked_points = []
        self.missed_frames_count = 0
        self.is_active = False

        if not frame_detections:
            return None

        total_frames = len(frame_detections)
        detected_count = 0
        interpolated_count = 0

        for frame_id, detections in frame_detections:
            if not self.is_active:
                # Find first confident detection to initialize tracker
                best_det = self._select_best_detection(detections)
                if best_det is not None:
                    self.kalman = self._init_kalman(best_det.center[0], best_det.center[1])
                    self.is_active = True
                    self.tracked_points.append(
                        TrackedPoint(
                            frame_id=frame_id,
                            x=best_det.center[0],
                            y=best_det.center[1],
                            vx=0.0,
                            vy=0.0,
                            confidence=best_det.confidence,
                            is_interpolated=False
                        )
                    )
                    detected_count += 1
            else:
                # Kalman Predict step
                prediction = self.kalman.predict()
                pred_x, pred_y = float(prediction[0][0]), float(prediction[1][0])
                pred_vx, pred_vy = float(prediction[2][0]), float(prediction[3][0])

                # Associate detection nearest to prediction within gating distance
                matched_det = self._associate_detection((pred_x, pred_y), detections)

                if matched_det is not None:
                    # Kalman Correct step
                    measurement = np.array([[matched_det.center[0]], [matched_det.center[1]]], dtype=np.float32)
                    self.kalman.correct(measurement)
                    state = self.kalman.statePost
                    cx, cy = float(state[0][0]), float(state[1][0])
                    vx, vy = float(state[2][0]), float(state[3][0])

                    self.tracked_points.append(
                        TrackedPoint(
                            frame_id=frame_id,
                            x=cx,
                            y=cy,
                            vx=vx,
                            vy=vy,
                            confidence=matched_det.confidence,
                            is_interpolated=False
                        )
                    )
                    detected_count += 1
                    self.missed_frames_count = 0
                else:
                    # Missed detection: use prediction up to max_missed_frames
                    self.missed_frames_count += 1
                    if self.missed_frames_count <= self.max_missed_frames:
                        # Decay confidence during occlusion
                        decay_conf = max(0.1, 0.8 - (self.missed_frames_count * 0.15))
                        self.tracked_points.append(
                            TrackedPoint(
                                frame_id=frame_id,
                                x=pred_x,
                                y=pred_y,
                                vx=pred_vx,
                                vy=pred_vy,
                                confidence=decay_conf,
                                is_interpolated=True
                            )
                        )
                        interpolated_count += 1
                    else:
                        # Track lost due to prolonged occlusion
                        logger.debug(f"Track lost at frame {frame_id} after {self.missed_frames_count} missed frames.")

        if len(self.tracked_points) < self.min_track_length:
            logger.warning(f"Track rejected: length {len(self.tracked_points)} < min {self.min_track_length}")
            return None

        start_f = self.tracked_points[0].frame_id
        end_f = self.tracked_points[-1].frame_id
        track_total_len = len(self.tracked_points)

        coverage = float(detected_count / track_total_len) if track_total_len > 0 else 0.0
        avg_conf = float(np.mean([p.confidence for p in self.tracked_points]))
        track_conf = min(1.0, max(0.0, avg_conf * 0.7 + coverage * 0.3))

        return BallTrack(
            track_id=track_id,
            points=self.tracked_points,
            start_frame=start_f,
            end_frame=end_f,
            total_frames=track_total_len,
            detected_count=detected_count,
            interpolated_count=interpolated_count,
            coverage_ratio=coverage,
            track_confidence=track_conf
        )

    def _associate_detection(
        self, predicted_pos: Tuple[float, float], detections: List[BallDetection]
    ) -> Optional[BallDetection]:
        """Finds closest detection to predicted position within gating threshold."""
        if not detections:
            return None

        px, py = predicted_pos
        best_det = None
        min_dist = float("inf")

        for det in detections:
            cx, cy = det.center
            dist = np.hypot(cx - px, cy - py)
            if dist <= self.gating_threshold_px and dist < min_dist:
                min_dist = dist
                best_det = det

        return best_det

    def _select_best_detection(self, detections: List[BallDetection]) -> Optional[BallDetection]:
        """Selects highest confidence detection to start tracking."""
        if not detections:
            return None
        valid = [d for d in detections if d.confidence >= 0.4]
        if not valid:
            return None
        valid.sort(key=lambda d: d.confidence, reverse=True)
        return valid[0]
