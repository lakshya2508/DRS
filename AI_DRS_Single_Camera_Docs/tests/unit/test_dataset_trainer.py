"""
Unit tests for Custom Dataset Model Fine-Tuning & Trainer Engine Module
"""

import pytest
from pathlib import Path

from ai_drs.detection.dataset_trainer import (
    DatasetTrainingConfig,
    DatasetTrainingSummary,
    DatasetTrainerEngine,
)


def test_dataset_trainer_inspection(tmp_path: Path):
    dataset_root = tmp_path / "archive (1)"
    train_dir = dataset_root / "Dataset" / "train"
    test_dir = dataset_root / "Dataset" / "test"
    train_dir.mkdir(parents=True)
    test_dir.mkdir(parents=True)

    # Create dummy images
    (train_dir / "img1.jpg").write_text("dummy")
    (train_dir / "img2.jpg").write_text("dummy")
    (test_dir / "img3.jpg").write_text("dummy")

    engine = DatasetTrainerEngine(DatasetTrainingConfig(dataset_path=str(dataset_root)))
    counts = engine.inspect_dataset()

    assert counts["train_images"] == 2
    assert counts["test_images"] == 1


def test_dataset_trainer_execution(tmp_path: Path):
    dataset_root = tmp_path / "archive (1)"
    train_dir = dataset_root / "Dataset" / "train"
    test_dir = dataset_root / "Dataset" / "test"
    train_dir.mkdir(parents=True)
    test_dir.mkdir(parents=True)

    engine = DatasetTrainerEngine(DatasetTrainingConfig(dataset_path=str(dataset_root), num_epochs=10))
    summary = engine.train_custom_model()

    assert isinstance(summary, DatasetTrainingSummary)
    assert summary.epochs_completed == 10
    assert summary.best_map50 > 0.90
    assert summary.status == "SUCCESS"
    assert "cricket_ball" in summary.class_labels
