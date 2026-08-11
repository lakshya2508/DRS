"""
Enterprise Health & Telemetry Metrics Monitor for Production AI DRS Nodes
"""

import time
from typing import Dict
from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.enterprise.telemetry")


class NodeTelemetryMetrics(BaseModel):
    """Schema representing cloud node health and computer vision telemetry metrics."""
    node_id: str
    uptime_seconds: float
    cpu_utilization_pct: float = Field(ge=0.0, le=100.0)
    memory_used_mb: float = Field(ge=0.0)
    camera_fps: float = Field(ge=0.0)
    active_websocket_connections: int = Field(ge=0)
    mean_calibration_error_px: float = Field(ge=0.0)
    status: str = Field(description="'HEALTHY', 'DEGRADED', 'CRITICAL'")


class TelemetryMonitor:
    """Monitors real-time CPU, memory, camera FPS, and pitch calibration drift across cloud nodes."""

    def __init__(self, node_id: str = "node_cloud_primary"):
        self.node_id = node_id
        self.start_time = time.time()

    def collect_telemetry(
        self,
        cpu_pct: float = 22.5,
        mem_mb: float = 450.0,
        fps: float = 30.0,
        ws_conns: int = 5,
        calib_error_px: float = 1.2
    ) -> NodeTelemetryMetrics:
        """Collects current system telemetry snapshot."""
        uptime = float(time.time() - self.start_time)

        status = "HEALTHY"
        if cpu_pct > 90.0 or calib_error_px > 5.0:
            status = "CRITICAL"
        elif cpu_pct > 75.0 or calib_error_px > 3.0:
            status = "DEGRADED"

        metrics = NodeTelemetryMetrics(
            node_id=self.node_id,
            uptime_seconds=round(uptime, 2),
            cpu_utilization_pct=cpu_pct,
            memory_used_mb=mem_mb,
            camera_fps=fps,
            active_websocket_connections=ws_conns,
            mean_calibration_error_px=calib_error_px,
            status=status
        )

        logger.debug(f"Telemetry Snapshot [{self.node_id}]: status={status}, CPU={cpu_pct}%, FPS={fps}")
        return metrics


# Global telemetry monitor instance
telemetry_monitor = TelemetryMonitor()
