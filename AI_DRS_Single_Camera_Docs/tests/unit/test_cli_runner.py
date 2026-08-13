"""
Unit tests for AI DRS Master CLI Entry Point Runner Module
"""

import sys
import pytest
from unittest.mock import patch

from scripts.run_ai_drs import main


def test_cli_runner_certify_command(capsys):
    test_args = ["run_ai_drs.py", "certify"]
    with patch.object(sys, "argv", test_args):
        main()
    captured = capsys.readouterr()
    assert "100-MILESTONE MASTER SYSTEM CERTIFICATION" in captured.out
    assert "Passed Milestones: 100 / 100" in captured.out


def test_cli_runner_train_command(capsys, tmp_path):
    dataset_dir = tmp_path / "archive (1)"
    dataset_dir.mkdir(parents=True)

    test_args = ["run_ai_drs.py", "train", "--dataset", str(dataset_dir), "--epochs", "5"]
    with patch.object(sys, "argv", test_args):
        main()
    captured = capsys.readouterr()
    assert "Model Fine-Tuning Complete" in captured.out
    assert "Best mAP@50:" in captured.out
