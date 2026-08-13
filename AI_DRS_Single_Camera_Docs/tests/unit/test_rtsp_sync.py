"""
Unit tests for Multi-Camera RTSP Network Stream Sync Engine Module
"""

import pytest

from ai_drs.ingestion.rtsp_stream_sync import RTSPStreamSyncEngine, SynchronizedFrameBatch


def test_rtsp_stream_sync_success():
    cameras = ["CAM_01", "CAM_02", "CAM_03"]
    engine = RTSPStreamSyncEngine(cameras)

    engine.push_frame_timestamp("CAM_01", 1000.0)
    engine.push_frame_timestamp("CAM_02", 1001.5)
    engine.push_frame_timestamp("CAM_03", 1002.0)

    batch = engine.get_synchronized_batch(tolerance_ms=5.0)

    assert isinstance(batch, SynchronizedFrameBatch)
    assert batch.is_fully_synchronized is True
    assert batch.max_jitter_ms == 2.0
    assert len(batch.camera_ids) == 3


def test_rtsp_stream_sync_missing_buffer():
    engine = RTSPStreamSyncEngine(["CAM_01", "CAM_02"])
    engine.push_frame_timestamp("CAM_01", 1000.0)
    assert engine.get_synchronized_batch() is None
