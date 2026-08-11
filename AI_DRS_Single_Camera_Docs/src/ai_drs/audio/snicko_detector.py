"""
UltraEdge Snicko Audio Peak Processing Engine (Bandpass Filter & STFT Spike Analysis)
"""

from typing import List, Optional
import numpy as np
from pydantic import BaseModel, Field
from scipy.signal import butter, filtfilt

from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.audio.snicko")


class AudioEdgeEvent(BaseModel):
    """Schema representing an UltraEdge Snicko audio impact event."""
    frame_id: int = Field(ge=0)
    timestamp_s: float = Field(ge=0.0)
    is_edge_detected: bool
    snicko_spike_ratio: float = Field(ge=0.0)
    high_freq_power: float = Field(ge=0.0)


class SnickoAudioDetector:
    """UltraEdge Audio Detector analyzing high-frequency acoustic spikes for ball-bat edge detection."""

    def __init__(
        self,
        sample_rate: int = 44100,
        low_cutoff_hz: float = 2000.0,
        high_cutoff_hz: float = 8000.0,
        spike_threshold_ratio: float = 3.5
    ):
        self.sample_rate = sample_rate
        self.low_cutoff_hz = low_cutoff_hz
        self.high_cutoff_hz = high_cutoff_hz
        self.spike_threshold_ratio = spike_threshold_ratio

    def bandpass_filter(self, audio_data: np.ndarray) -> np.ndarray:
        """Applies 4th-order Butterworth bandpass filter to isolate 2kHz-8kHz frequencies."""
        nyquist = 0.5 * self.sample_rate
        low = self.low_cutoff_hz / nyquist
        high = self.high_cutoff_hz / nyquist
        b, a = butter(4, [low, high], btype="band")
        return filtfilt(b, a, audio_data)

    def analyze_audio_waveform(
        self,
        audio_data: np.ndarray,
        fps: float = 30.0,
        start_frame: int = 0
    ) -> List[AudioEdgeEvent]:
        """Analyzes audio waveform and returns frame-aligned Snicko edge events."""
        if len(audio_data) == 0:
            return []

        # Filter audio to high-frequency band
        filtered = self.bandpass_filter(audio_data)
        energy = filtered ** 2

        samples_per_frame = int(round(self.sample_rate / fps))
        total_frames = len(energy) // samples_per_frame

        if total_frames == 0:
            return []

        frame_energies: List[float] = []
        for i in range(total_frames):
            segment = energy[i * samples_per_frame: (i + 1) * samples_per_frame]
            frame_energies.append(float(np.mean(segment)))

        # Baseline noise floor (median energy)
        noise_floor = float(np.median(frame_energies)) if frame_energies else 1e-6
        if noise_floor == 0:
            noise_floor = 1e-6

        events: List[AudioEdgeEvent] = []

        for i, eng in enumerate(frame_energies):
            spike_ratio = float(eng / noise_floor)
            is_edge = spike_ratio >= self.spike_threshold_ratio
            frame_idx = start_frame + i
            timestamp = float(frame_idx / fps)

            if is_edge:
                logger.info(
                    f"UltraEdge Snicko Spike Detected [Frame {frame_idx}]: "
                    f"t={timestamp:.3f}s, spike_ratio={spike_ratio:.2f}x noise floor"
                )

            events.append(
                AudioEdgeEvent(
                    frame_id=frame_idx,
                    timestamp_s=timestamp,
                    is_edge_detected=is_edge,
                    snicko_spike_ratio=spike_ratio,
                    high_freq_power=eng
                )
            )

        return events
