"""
Unit tests for Ball Detector Module
"""

from unittest.mock import MagicMock, patch
import numpy as np
import cv2
import pytest

from ai_drs.detection.ball_detector import (
    ClassicalBallDetector,
    YOLOBallDetector,
    BallDetection,
    BallDetectorConfig,
)


@pytest.fixture
def synthetic_ball_frame():
    """Creates a synthetic BGR frame containing a white ball circle."""
    height, width = 720, 1280
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    frame[:] = (40, 100, 40)  # Green grass pitch background

    # Draw white ball at (640, 360) with radius 15
    cv2.circle(frame, (640, 360), 15, (240, 240, 240), -1)
    return frame


@pytest.fixture
def synthetic_red_ball_frame():
    """Creates a synthetic BGR frame containing a red ball circle."""
    height, width = 720, 1280
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    frame[:] = (50, 120, 50)  # Pitch background

    # Draw red ball in BGR format: (0, 0, 220)
    cv2.circle(frame, (400, 300), 15, (20, 20, 220), -1)
    return frame


def test_classical_detector_white_ball(synthetic_ball_frame):
    detector = ClassicalBallDetector()
    best_det = detector.detect_best(synthetic_ball_frame, frame_id=5, ball_color="white")

    assert best_det is not None
    assert isinstance(best_det, BallDetection)
    assert best_det.frame_id == 5
    assert abs(best_det.center[0] - 640.0) < 3.0
    assert abs(best_det.center[1] - 360.0) < 3.0
    assert abs(best_det.radius - 15.0) < 3.0
    assert best_det.confidence >= 0.5


def test_classical_detector_red_ball(synthetic_red_ball_frame):
    detector = ClassicalBallDetector()
    best_det = detector.detect_best(synthetic_red_ball_frame, frame_id=1, ball_color="red")

    assert best_det is not None
    assert abs(best_det.center[0] - 400.0) < 3.0
    assert abs(best_det.center[1] - 300.0) < 3.0


def test_blank_frame_no_detection():
    height, width = 720, 1280
    blank = np.zeros((height, width, 3), dtype=np.uint8)
    blank[:] = (40, 100, 40)

    detector = ClassicalBallDetector()
    detections = detector.detect(blank, frame_id=0)
    assert len(detections) == 0

    best = detector.detect_best(blank, frame_id=0)
    assert best is None

    empty = detector.detect(None)
    assert empty == []


def test_motion_difference_detection():
    detector = ClassicalBallDetector()
    height, width = 720, 1280

    prev_frame = np.zeros((height, width, 3), dtype=np.uint8)
    prev_frame[:] = (40, 100, 40)
    cv2.circle(prev_frame, (600, 360), 15, (240, 240, 240), -1)

    curr_frame = np.zeros((height, width, 3), dtype=np.uint8)
    curr_frame[:] = (40, 100, 40)
    cv2.circle(curr_frame, (640, 360), 15, (240, 240, 240), -1)

    detections = detector.detect(curr_frame, frame_id=10, prev_image=prev_frame)
    assert len(detections) > 0
    best = detections[0]
    assert abs(best.center[0] - 640.0) < 3.0


def test_yolo_detector_unweighted():
    yolo_detector = YOLOBallDetector(weights_path="non_existent_weights.pt")
    dummy_frame = np.zeros((720, 1280, 3), dtype=np.uint8)

    detections = yolo_detector.detect(dummy_frame, frame_id=0)
    assert len(detections) == 0


def test_yolo_detector_mocked():
    with patch("pathlib.Path.exists", return_value=True):
        mock_yolo_cls = MagicMock()
        mock_yolo_inst = MagicMock()

        # Mock YOLO detection result bounding box
        mock_box = MagicMock()
        mock_box.conf = [0.85]
        mock_box.xyxy = [[100.0, 200.0, 140.0, 240.0]]

        mock_result = MagicMock()
        mock_result.boxes = [mock_box]

        mock_yolo_inst.return_value = [mock_result]
        mock_yolo_cls.return_value = mock_yolo_inst

        with patch.dict("sys.modules", {"ultralytics": MagicMock(YOLO=mock_yolo_cls)}):
            detector = YOLOBallDetector(weights_path="dummy.pt")
            dummy_frame = np.zeros((720, 1280, 3), dtype=np.uint8)
            dets = detector.detect(dummy_frame, frame_id=3)

            assert len(dets) == 1
            assert dets[0].confidence == 0.85
            assert dets[0].center == (120.0, 220.0)
            assert dets[0].radius == 20.0
