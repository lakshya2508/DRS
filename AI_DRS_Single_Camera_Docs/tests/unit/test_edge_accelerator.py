"""
Unit tests for Edge AI Hardware Acceleration Engine Wrapper Module
"""

import pytest

from ai_drs.detection.edge_accelerator import EdgeAcceleratorConfig, EdgeAcceleratorEngine


def test_edge_accelerator_jetson():
    cfg = EdgeAcceleratorEngine.get_hardware_accelerator("NVIDIA_JETSON")
    assert isinstance(cfg, EdgeAcceleratorConfig)
    assert cfg.execution_provider == "TensorrtExecutionProvider"
    assert cfg.fp16_enabled is True
    assert cfg.mean_inference_latency_ms < 5.0


def test_edge_accelerator_pi5():
    cfg = EdgeAcceleratorEngine.get_hardware_accelerator("RASPBERRY_PI_5")
    assert cfg.execution_provider == "OpenVINOExecutionProvider"
    assert cfg.fp16_enabled is True


def test_edge_accelerator_cpu():
    cfg = EdgeAcceleratorEngine.get_hardware_accelerator("GENERIC_CPU")
    assert cfg.execution_provider == "CPUExecutionProvider"
    assert cfg.fp16_enabled is False
