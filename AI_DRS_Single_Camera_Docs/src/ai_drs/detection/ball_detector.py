"""
Ball Detection Module for AI DRS (Classical CV Baseline & Deep Learning Detector Interface)
"""

from pathlib import Path
from typing import List, Optional, Tuple, Union
import cv2
import numpy as np
from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.detection.ball")


class BallDetection(BaseModel):
    """Schema representing a detected ball instance in a single frame."""
    frame_id: int = Field(ge=0, description="Frame index")
    bbox: Tuple[float, float, float, float] = Field(description="Bounding box (x_min, y_min, x_max, y_max)")
    center: Tuple[float, float] = Field(description="Ball center pixel coordinates (cx, cy)")
    radius: float = Field(ge=0.0, description="Estimated ball radius in pixels")
    confidence: float = Field(ge=0.0, le=1.0, description="Detection confidence score")


class BallDetectorConfig(BaseModel):
    """Configuration for Classical CV Ball Detector."""
    min_radius_px: float = Field(default=3.0, ge=1.0)
    max_radius_px: float = Field(default=50.0, ge=2.0)
    min_circularity: float = Field(default=0.4, ge=0.0, le=1.0)
    min_confidence: float = Field(default=0.3, ge=0.0, le=1.0)

    # HSV thresholds for red cricket ball
    red_hsv_lower1: Tuple[int, int, int] = (0, 70, 50)
    red_hsv_upper1: Tuple[int, int, int] = (10, 255, 255)
    red_hsv_lower2: Tuple[int, int, int] = (170, 70, 50)
    red_hsv_upper2: Tuple[int, int, int] = (180, 255, 255)

    # HSV thresholds for white cricket ball
    white_hsv_lower: Tuple[int, int, int] = (0, 0, 160)
    white_hsv_upper: Tuple[int, int, int] = (180, 60, 255)


class ClassicalBallDetector:
    """Classical Computer Vision Ball Detector Baseline using HSV segmentation, circularity, and motion difference."""

    def __init__(self, config: Optional[BallDetectorConfig] = None):
        self.config = config or BallDetectorConfig()

    def get_color_mask(self, hsv_image: np.ndarray, ball_color: str = "white") -> np.ndarray:
        """Generates binary mask for specified ball color in HSV space."""
        if ball_color.lower() == "red":
            mask1 = cv2.inRange(hsv_image, np.array(self.config.red_hsv_lower1), np.array(self.config.red_hsv_upper1))
            mask2 = cv2.inRange(hsv_image, np.array(self.config.red_hsv_lower2), np.array(self.config.red_hsv_upper2))
            return cv2.bitwise_or(mask1, mask2)
        else:  # white ball (default)
            return cv2.inRange(hsv_image, np.array(self.config.white_hsv_lower), np.array(self.config.white_hsv_upper))

    def detect(
        self,
        image: np.ndarray,
        frame_id: int = 0,
        prev_image: Optional[np.ndarray] = None,
        ball_color: str = "white"
    ) -> List[BallDetection]:
        """Detects potential ball candidates in a single frame image."""
        if image is None or image.size == 0:
            return []

        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        color_mask = self.get_color_mask(hsv, ball_color=ball_color)

        # Morphological opening/closing to reduce noise
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_OPEN, kernel)
        color_mask = cv2.morphologyEx(color_mask, cv2.MORPH_CLOSE, kernel)

        # Motion mask if previous frame provided
        motion_mask = None
        if prev_image is not None and prev_image.shape == image.shape:
            gray_curr = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            gray_prev = cv2.cvtColor(prev_image, cv2.COLOR_BGR2GRAY)
            diff = cv2.absdiff(gray_curr, gray_prev)
            _, motion_mask = cv2.threshold(diff, 20, 255, cv2.THRESH_BINARY)
            combined_mask = cv2.bitwise_and(color_mask, motion_mask)
        else:
            combined_mask = color_mask

        contours, _ = cv2.findContours(combined_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Fallback to color_mask if combined_mask produced no contours when motion mask was applied
        if not contours and motion_mask is not None:
            contours, _ = cv2.findContours(color_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        detections: List[BallDetection] = []

        for cnt in contours:
            area = cv2.contourArea(cnt)
            perimeter = cv2.arcLength(cnt, True)
            if perimeter <= 0:
                continue

            # Circularity metric: 4 * pi * Area / (Perimeter^2)
            circularity = (4.0 * np.pi * area) / (perimeter * perimeter)
            if circularity < self.config.min_circularity:
                continue

            (cx, cy), radius = cv2.minEnclosingCircle(cnt)
            if not (self.config.min_radius_px <= radius <= self.config.max_radius_px):
                continue

            # Calculate bounding box
            x_min = max(0.0, float(cx - radius))
            y_min = max(0.0, float(cy - radius))
            x_max = min(float(image.shape[1]), float(cx + radius))
            y_max = min(float(image.shape[0]), float(cy + radius))

            # Confidence score combining circularity and radius fit
            conf = min(1.0, float(circularity * 0.7 + (1.0 - abs(radius - 15.0) / 30.0) * 0.3))
            conf = max(0.0, conf)

            if conf >= self.config.min_confidence:
                detections.append(
                    BallDetection(
                        frame_id=frame_id,
                        bbox=(x_min, y_min, x_max, y_max),
                        center=(float(cx), float(cy)),
                        radius=float(radius),
                        confidence=conf
                    )
                )

        # Sort detections by confidence descending
        detections.sort(key=lambda d: d.confidence, reverse=True)
        return detections

    def detect_best(
        self,
        image: np.ndarray,
        frame_id: int = 0,
        prev_image: Optional[np.ndarray] = None,
        ball_color: str = "white"
    ) -> Optional[BallDetection]:
        """Returns the highest confidence ball detection candidate in a frame, or None if not found."""
        candidates = self.detect(image, frame_id=frame_id, prev_image=prev_image, ball_color=ball_color)
        return candidates[0] if candidates else None


class YOLOBallDetector:
    """Wrapper for deep learning YOLO Ball Detector."""

    def __init__(self, weights_path: Optional[str] = None, confidence_threshold: float = 0.35):
        self.weights_path = weights_path
        self.confidence_threshold = confidence_threshold
        self.model = None

        if weights_path and Path(weights_path).exists():
            try:
                from ultralytics import YOLO
                self.model = YOLO(weights_path)
                logger.info(f"Loaded YOLO ball detector model weights from {weights_path}")
            except Exception as e:
                logger.warning(f"Failed to load YOLO model: {e}")
        else:
            logger.info("YOLOBallDetector initialized without weights (will fallback or return empty).")

    def detect(self, image: np.ndarray, frame_id: int = 0) -> List[BallDetection]:
        """Runs YOLO inference if model is loaded, else returns empty list."""
        if self.model is None or image is None or image.size == 0:
            return []

        results = self.model(image, verbose=False)
        detections: List[BallDetection] = []

        for r in results:
            for box in r.boxes:
                conf = float(box.conf[0])
                if conf < self.confidence_threshold:
                    continue
                x1, y1, x2, y2 = [float(v) for v in box.xyxy[0]]
                cx = (x1 + x2) / 2.0
                cy = (y1 + y2) / 2.0
                radius = max((x2 - x1), (y2 - y1)) / 2.0

                detections.append(
                    BallDetection(
                        frame_id=frame_id,
                        bbox=(x1, y1, x2, y2),
                        center=(cx, cy),
                        radius=radius,
                        confidence=conf
                    )
                )

        detections.sort(key=lambda d: d.confidence, reverse=True)
        return detections
