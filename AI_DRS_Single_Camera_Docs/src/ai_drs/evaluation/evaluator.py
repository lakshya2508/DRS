"""
System Evaluation and Benchmark Metrics Module for AI DRS
"""

import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Union
import numpy as np
from pydantic import BaseModel, Field

from ai_drs.api.review_service import ReviewPipelineService
from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.evaluation")


class GroundTruthDelivery(BaseModel):
    """Schema representing a ground truth delivery benchmark sample."""
    delivery_id: str
    video_filename: str
    ground_truth_result: str = Field(description="'OUT', 'NOT_OUT', or 'INCONCLUSIVE'")
    pitching_zone: Optional[str] = None
    impact_zone: Optional[str] = None
    wicket_hit_result: Optional[str] = None


class EvaluationMetrics(BaseModel):
    """Schema representing overall system benchmark metrics."""
    total_deliveries: int = Field(ge=0)
    correct_decisions: int = Field(ge=0)
    incorrect_decisions: int = Field(ge=0)
    inconclusive_decisions: int = Field(ge=0)
    accuracy: float = Field(ge=0.0, le=1.0)
    inconclusive_rate: float = Field(ge=0.0, le=1.0)
    avg_latency_seconds: float = Field(ge=0.0)
    confusion_matrix: Dict[str, Dict[str, int]] = Field(default_factory=dict)


class SystemEvaluator:
    """Benchmark evaluation runner evaluating AI DRS pipeline against held-out delivery datasets."""

    def __init__(self, service: Optional[ReviewPipelineService] = None):
        self.service = service or ReviewPipelineService()

    def evaluate_dataset(
        self, deliveries: List[GroundTruthDelivery], data_dir: Union[str, Path]
    ) -> EvaluationMetrics:
        """Evaluates a batch of ground-truth deliveries and computes metrics."""
        base_dir = Path(data_dir).resolve()
        total = len(deliveries)
        if total == 0:
            return EvaluationMetrics(
                total_deliveries=0,
                correct_decisions=0,
                incorrect_decisions=0,
                inconclusive_decisions=0,
                accuracy=0.0,
                inconclusive_rate=0.0,
                avg_latency_seconds=0.0,
                confusion_matrix={}
            )

        correct = 0
        incorrect = 0
        inconclusive = 0
        latencies: List[float] = []

        labels = ["OUT", "NOT_OUT", "INCONCLUSIVE"]
        conf_mat = {gt: {pred: 0 for pred in labels} for gt in labels}

        for item in deliveries:
            video_path = base_dir / item.video_filename
            t0 = time.time()
            res = self.service.process_video(video_path)
            t1 = time.time()

            latencies.append(t1 - t0)
            pred = res.result
            gt = item.ground_truth_result

            if gt in conf_mat and pred in conf_mat[gt]:
                conf_mat[gt][pred] += 1

            if pred == "INCONCLUSIVE":
                inconclusive += 1
            elif pred == gt:
                correct += 1
            else:
                incorrect += 1

        acc = (correct / (total - inconclusive)) if (total - inconclusive) > 0 else 0.0
        inc_rate = inconclusive / total
        avg_lat = float(np.mean(latencies)) if latencies else 0.0

        logger.info(
            f"Evaluated {total} deliveries: correct={correct}, incorrect={incorrect}, "
            f"inconclusive={inconclusive}, acc={acc:.1%}, inc_rate={inc_rate:.1%}, avg_lat={avg_lat:.2f}s"
        )

        return EvaluationMetrics(
            total_deliveries=total,
            correct_decisions=correct,
            incorrect_decisions=incorrect,
            inconclusive_decisions=inconclusive,
            accuracy=acc,
            inconclusive_rate=inc_rate,
            avg_latency_seconds=avg_lat,
            confusion_matrix=conf_mat
        )

    @staticmethod
    def save_report(metrics: EvaluationMetrics, output_path: Union[str, Path]) -> Path:
        """Saves evaluation report to JSON file."""
        path = Path(output_path).resolve()
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(metrics.model_dump_json(indent=2))
        return path
