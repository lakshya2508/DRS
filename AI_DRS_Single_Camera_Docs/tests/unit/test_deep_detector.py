"""
Unit tests for Deep Learning Ball Detector and MediaPipe Pose Estimator Module
"""

import numpy as np
import pytest

from ai_drs.detection.ball_detector import BallDetection
from ai_drs.detection.deep_detector import (
    BatterPoseEstimation,
    DeepBallDetector,
    MediaPipePoseDetector,
)


def test_deep_ball_detector_fallback():
    detector = DeepBallDetector(model_path=None)
    frame = np.zeros((720, 1280, 3), dtype=np.uint8)

    detections = detector.detect_ball(frame, frame_id=5)

    assert detections[0].center == (640.0, 360.0)
    assert detections[0].confidence == 0.88



def test_mediapipe_pose_detector():
    pose_detector = MediaPipePoseDetector()
    frame = np.zeros((720, 1280, 3), dtype=np.uint8)

    # Shot offered test (bat close to hand)
    pose_shot = pose_detector.analyze_shot_offered(frame, frame_id=1, bat_position_px=(600, 480))
    assert isinstance(pose_shot, BatterPoseEstimation)
    assert pose_shot.shot_offered is True
    assert pose_shot.confidence >= 0.50

    # No shot offered test (bat far from hand / padded away)
    pose_noshot = pose_detector.analyze_shot_offered(frame, frame_id=1, bat_position_px=(1200, 100))
    assert pose_noshot.shot_offered is False
