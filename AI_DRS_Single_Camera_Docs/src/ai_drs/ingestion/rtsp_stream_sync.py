"""
Multi-Camera RTSP Network Stream Sync Engine
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.ingestion.rtsp_sync")


class SynchronizedFrameBatch(BaseModel):
    """Schema representing synchronized multi-camera frame batch across RTSP streams."""
    timestamp_ntp_ms: float
    camera_ids: List[str]
    is_fully_synchronized: bool
    max_jitter_ms: float = Field(ge=0.0)


class RTSPStreamSyncEngine:
    """Synchronizes RTSP IP video streams using millisecond NTP timestamps."""

    def __init__(self, camera_ids: List[str]):
        self.expected_cameras = camera_ids
        # camera_id -> List of (ntp_timestamp_ms, frame)
        self.buffers: Dict[str, List[float]] = {cid: [] for cid in camera_ids}

    def push_frame_timestamp(self, camera_id: str, ntp_ms: float):
        """Pushes an incoming frame NTP timestamp into stream buffer."""
        if camera_id in self.buffers:
            self.buffers[camera_id].append(ntp_ms)

    def get_synchronized_batch(self, tolerance_ms: float = 5.0) -> Optional[SynchronizedFrameBatch]:
        """Aligns frames across all cameras within NTP tolerance_ms."""
        if not all(self.buffers[cid] for cid in self.expected_cameras):
            return None

        # Take earliest timestamps across buffers
        ts_map = {cid: self.buffers[cid][0] for cid in self.expected_cameras}
        min_ts = min(ts_map.values())
        max_ts = max(ts_map.values())

        jitter = max_ts - min_ts
        is_synced = jitter <= tolerance_ms

        if is_synced:
            for cid in self.expected_cameras:
                self.buffers[cid].pop(0)

            logger.debug(f"RTSP Multi-Cam Sync Batch: NTP={min_ts:.1f}ms, jitter={jitter:.2f}ms")
            return SynchronizedFrameBatch(
                timestamp_ntp_ms=min_ts,
                camera_ids=list(self.expected_cameras),
                is_fully_synchronized=True,
                max_jitter_ms=round(jitter, 2)
            )

        return None
