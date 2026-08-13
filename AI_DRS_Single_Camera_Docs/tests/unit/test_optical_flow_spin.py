"""
Unit tests for Dense Optical Flow Ball Seam Spin Rate Estimator Module
"""

import numpy as np
import pytest

from ai_drs.vision.optical_flow_spin import BallSpinEstimate, OpticalFlowSpinEstimator


def test_optical_flow_spin_estimation():
    estimator = OpticalFlowSpinEstimator()

    # Synthetic prev/curr crop with motion shift
    prev_crop = np.zeros((40, 40, 3), dtype=np.uint8)
    prev_crop[15:25, 15:25] = 255

    curr_crop = np.zeros((40, 40, 3), dtype=np.uint8)
    curr_crop[17:27, 17:27] = 255

    estimate = estimator.estimate_ball_spin(prev_crop, curr_crop, fps=240.0, ball_radius_px=20.0)

    assert isinstance(estimate, BallSpinEstimate)
    assert estimate.spin_rpm >= 0.0
    assert 0.0 <= estimate.confidence <= 1.0


def test_empty_crop_spin_estimation():
    estimator = OpticalFlowSpinEstimator()
    empty = np.zeros((0, 0, 3), dtype=np.uint8)
    estimate = estimator.estimate_ball_spin(empty, empty)
    assert estimate.spin_rpm == 0.0
    assert estimate.confidence == 0.0
