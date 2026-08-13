"""
Match Replay Timeline & DVR Scrubbing Controller Module
"""

from typing import List, Optional
from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.api.replay")


class ReplayFrameState(BaseModel):
    """Schema representing frame playback scrubbing state."""
    match_id: str
    current_frame: int
    total_frames: int
    playback_speed: float = Field(default=1.0)
    is_paused: bool = False
    bookmarked_event: Optional[str] = None


class MatchReplayController:
    """Manages DVR timeline scrubbing, variable playback speed (0.25x - 2.0x), and event bookmarking."""

    def __init__(self, match_id: str, total_frames: int = 1800):
        self.match_id = match_id
        self.total_frames = total_frames
        self.current_frame = 0
        self.playback_speed = 1.0
        self.is_paused = False

    def seek_to_frame(self, frame_index: int) -> ReplayFrameState:
        """Seeks DVR replay timeline to specific frame index."""
        self.current_frame = min(self.total_frames, max(0, frame_index))
        logger.debug(f"Replay DVR Seek [{self.match_id}]: Frame {self.current_frame}/{self.total_frames}")

        return ReplayFrameState(
            match_id=self.match_id,
            current_frame=self.current_frame,
            total_frames=self.total_frames,
            playback_speed=self.playback_speed,
            is_paused=self.is_paused
        )

    def set_speed(self, speed: float) -> ReplayFrameState:
        """Sets playback speed multiplier (0.25, 0.5, 1.0, 2.0)."""
        self.playback_speed = min(4.0, max(0.1, speed))
        return ReplayFrameState(
            match_id=self.match_id,
            current_frame=self.current_frame,
            total_frames=self.total_frames,
            playback_speed=self.playback_speed,
            is_paused=self.is_paused
        )
