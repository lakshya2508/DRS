"""
Automated MP4 Highlight Video Montage Stitcher for AI DRS
"""

from typing import List, Optional
import cv2
from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger
from ai_drs.evaluation.highlight_generator import HighlightClip

logger = setup_logger("ai_drs.evaluation.montage")


class MontageExportResult(BaseModel):
    """Schema representing generated highlight video montage metadata."""
    montage_id: str
    output_video_path: str
    total_clips_stitched: int
    duration_seconds: float


class HighlightMontageBuilder:
    """Stitches frame-aligned delivery clips into a unified MP4 highlight video montage."""

    @staticmethod
    def build_highlight_montage(
        input_video_path: str,
        output_video_path: str,
        clips: List[HighlightClip]
    ) -> MontageExportResult:
        """Reads input delivery video, extracts highlight frame ranges, and writes output MP4 montage."""
        cap = cv2.VideoCapture(input_video_path)
        if not cap.isOpened() or not clips:
            logger.warning(f"Could not open video '{input_video_path}' or no clips provided. Generating manifest stub.")
            return MontageExportResult(
                montage_id="montage_stub",
                output_video_path=output_video_path,
                total_clips_stitched=len(clips),
                duration_seconds=0.0
            )

        fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) or 1280
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) or 720

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(output_video_path, fourcc, fps, (w, h))

        total_frames_written = 0
        for clip in clips:
            cap.set(cv2.CAP_PROP_POS_FRAMES, clip.frame_start)
            curr = clip.frame_start
            while curr <= clip.frame_end:
                ret, frame = cap.read()
                if not ret:
                    break
                out.write(frame)
                total_frames_written += 1
                curr += 1

        cap.release()
        out.release()

        duration = float(total_frames_written / fps)
        logger.info(
            f"Built Highlight Video Montage [{output_video_path}]: "
            f"{len(clips)} clips, {total_frames_written} frames ({duration:.1f}s)"
        )

        return MontageExportResult(
            montage_id="montage_001",
            output_video_path=output_video_path,
            total_clips_stitched=len(clips),
            duration_seconds=round(duration, 1)
        )
