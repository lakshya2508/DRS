"""
Unit tests for System Evaluation and Benchmark Module
"""

import tempfile
from pathlib import Path
import pytest

from ai_drs.evaluation.evaluator import (
    SystemEvaluator,
    GroundTruthDelivery,
    EvaluationMetrics,
)
from ai_drs.ingestion.video_ingestion import create_synthetic_video


def test_system_evaluator_synthetic_batch():
    with tempfile.TemporaryDirectory() as tmpdir:
        data_dir = Path(tmpdir)
        v1 = create_synthetic_video(data_dir / "deliv_1.mp4", num_frames=15)
        v2 = create_synthetic_video(data_dir / "deliv_2.mp4", num_frames=15)

        deliveries = [
            GroundTruthDelivery(delivery_id="D1", video_filename="deliv_1.mp4", ground_truth_result="OUT"),
            GroundTruthDelivery(delivery_id="D2", video_filename="deliv_2.mp4", ground_truth_result="NOT_OUT"),
        ]

        evaluator = SystemEvaluator()
        metrics = evaluator.evaluate_dataset(deliveries, data_dir=data_dir)

        assert isinstance(metrics, EvaluationMetrics)
        assert metrics.total_deliveries == 2
        assert metrics.avg_latency_seconds >= 0.0
        assert "OUT" in metrics.confusion_matrix

        # Test report saving
        report_path = data_dir / "report.json"
        saved = SystemEvaluator.save_report(metrics, report_path)
        assert saved.exists()


def test_empty_dataset_evaluation():
    evaluator = SystemEvaluator()
    metrics = evaluator.evaluate_dataset([], data_dir=".")
    assert metrics.total_deliveries == 0
    assert metrics.accuracy == 0.0
