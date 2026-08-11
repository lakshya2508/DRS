"""
Unit tests for Enterprise Health & Telemetry Metrics Monitor Module
"""

import pytest

from ai_drs.enterprise.telemetry_monitor import (
    NodeTelemetryMetrics,
    TelemetryMonitor,
)


def test_telemetry_monitor_healthy():
    monitor = TelemetryMonitor("node_test_01")
    metrics = monitor.collect_telemetry(cpu_pct=30.0, mem_mb=512.0, fps=30.0, calib_error_px=1.1)

    assert isinstance(metrics, NodeTelemetryMetrics)
    assert metrics.node_id == "node_test_01"
    assert metrics.status == "HEALTHY"
    assert metrics.uptime_seconds >= 0.0


def test_telemetry_monitor_degraded_and_critical():
    monitor = TelemetryMonitor("node_test_02")

    # Degraded CPU
    metrics_deg = monitor.collect_telemetry(cpu_pct=80.0, calib_error_px=1.5)
    assert metrics_deg.status == "DEGRADED"

    # Critical Calibration Error
    metrics_crit = monitor.collect_telemetry(cpu_pct=40.0, calib_error_px=6.5)
    assert metrics_crit.status == "CRITICAL"
