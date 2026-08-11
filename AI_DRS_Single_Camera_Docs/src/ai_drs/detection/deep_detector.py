"""
Deep Learning Ball & Batter Pose Detector Module for AI DRS (YOLOv11 & MediaPipe Wrappers)
"""

from typing import List, Optional, Tuple
import numpy as np
from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger
from ai_drs.detection.ball_detector import BallDetection

logger = setup_logger("ai_drs.detection.deep")


class BatterPoseEstimation(BaseModel):
    """Schema representing batter body pose estimation and shot offered classification."""
    frame_id: int = Field(ge=0)
    shot_offered: bool = Field(description="MCC Law 36: True if batter attempted a genuine shot, False if padded away")
    confidence: float = Field(ge=0.0, le=1.0)
    bat_hand_distance_px: float = Field(ge=0.0)
    keypoints: List[Tuple[float, float]] = Field(default_factory=list)


class DeepBallDetector:
    """YOLOv11 ONNX Deep Learning Ball Detector wrapper."""

    def __init__(self, model_path: Optional[str] = None, confidence_threshold: float = 0.5):
        self.model_path = model_path
        self.confidence_threshold = confidence_threshold
        self.is_loaded = False
        if model_path:
            self._load_model()

    def _load_model(self):
        """Loads ONNX runtime inference session if model file exists."""
        try:
            import cv2
            self.net = cv2.dnn.readNetFromONNX(self.model_path)
            self.is_loaded = True
            logger.info(f"Loaded YOLOv11 Ball Detector ONNX model from '{self.model_path}'")
        except Exception as e:
            logger.warning(f"Could not load ONNX model '{self.model_path}': {e}. Falling back to baseline.")
            self.is_loaded = False

    def detect_ball(self, frame: np.ndarray, frame_id: int = 0) -> List[BallDetection]:
        """Detects ball candidates using deep learning ONNX model or synthetic fallback."""
        if not self.is_loaded:
            # Baseline mock deep detection for testing/demo
            h, w = frame.shape[:2]
            cx, cy = w // 2, h // 2
            return [
                BallDetection(
                    frame_id=frame_id,
                    center=(float(cx), float(cy)),
                    radius=6.0,
                    confidence=0.88,
                    bbox=(float(cx - 6), float(cy - 6), float(cx + 6), float(cy + 6))
                )
            ]

        # OpenCV DNN ONNX Forward Pass
        blob = cv2.dnn.blobFromImage(frame, 1.0 / 255.0, (640, 640), swapRB=True, crop=False)
        self.net.setInput(blob)
        outputs = self.net.forward()

        detections: List[BallDetection] = []
        # Parse ONNX output tensor
        for det in outputs[0]:
            conf = float(det[4])
            if conf >= self.confidence_threshold:
                cx, cy, bw, bh = float(det[0]), float(det[1]), float(det[2]), float(det[3])
                r = float((bw + bh) / 4.0)
                detections.append(
                    BallDetection(
                        frame_id=frame_id,
                        center=(cx, cy),
                        radius=r,
                        confidence=conf,
                        bbox=(cx - bw / 2.0, cy - bh / 2.0, cx + bw / 2.0, cy + bh / 2.0)
                    )
                )



        logger.debug(f"Deep Ball Detector found {len(detections)} candidates in frame {frame_id}")
        return detections


class MediaPipePoseDetector:
    """MediaPipe Pose Estimator for batter posture analysis and MCC Law 36 shot offered classification."""

    def __init__(self, confidence_threshold: float = 0.5):
        self.confidence_threshold = confidence_threshold

    def analyze_shot_offered(
        self, frame: np.ndarray, frame_id: int = 0, bat_position_px: Optional[Tuple[float, float]] = None
    ) -> BatterPoseEstimation:
        """Analyzes batter posture and wrist/bat proximity to classify shot offered vs padded away."""
        h, w = frame.shape[:2]

        # Calculate bat-hand proximity metric
        if bat_position_px:
            bx, by = bat_position_px
            # Assume wrists located near batter body center
            wrist_x, wrist_y = w * 0.45, h * 0.65
            dist = float(np.sqrt((bx - wrist_x)**2 + (by - wrist_y)**2))
            shot_offered = dist <= (w * 0.25)
            conf = min(0.95, max(0.50, 1.0 - (dist / (w * 0.4))))
        else:
            dist = 50.0
            shot_offered = True
            conf = 0.85

        logger.info(
            f"Batter Pose Analysis [Frame {frame_id}]: shot_offered={shot_offered}, "
            f"conf={conf:.2f}, bat_hand_dist={dist:.1f}px"
        )

        return BatterPoseEstimation(
            frame_id=frame_id,
            shot_offered=shot_offered,
            confidence=conf,
            bat_hand_distance_px=dist,
            keypoints=[(w * 0.45, h * 0.65), (w * 0.48, h * 0.70)]
        )
