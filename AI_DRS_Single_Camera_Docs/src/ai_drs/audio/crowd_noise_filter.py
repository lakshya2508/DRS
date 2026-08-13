"""
Stadium Crowd Noise Spectral Subtraction Filter Module
"""

from typing import Tuple
import numpy as np
from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.audio.crowd_filter")


class CrowdNoiseFilterResult(BaseModel):
    """Schema representing crowd noise reduction metrics."""
    original_snr_db: float
    filtered_snr_db: float
    noise_reduction_gain_db: float
    clean_audio_samples_count: int


class CrowdNoiseFilterEngine:
    """Filters out ambient stadium crowd roaring using spectral subtraction to isolate sharp Snicko impulse spikes."""

    @staticmethod
    def filter_crowd_noise(
        audio_signal: np.ndarray,
        sample_rate: int = 44100,
        alpha: float = 2.0
    ) -> Tuple[np.ndarray, CrowdNoiseFilterResult]:
        """Applies spectral subtraction algorithm to suppress continuous background stadium noise floor."""
        if audio_signal is None or len(audio_signal) == 0:
            return np.array([], dtype=np.float32), CrowdNoiseFilterResult(
                original_snr_db=0.0, filtered_snr_db=0.0, noise_reduction_gain_db=0.0, clean_audio_samples_count=0
            )

        signal = audio_signal.astype(np.float32)

        # Estimate background noise floor from first 10% of samples
        noise_estimation_len = max(10, int(len(signal) * 0.10))
        noise_floor_power = float(np.mean(np.square(signal[:noise_estimation_len]))) + 1e-8

        signal_power = float(np.mean(np.square(signal))) + 1e-8
        orig_snr = 10.0 * np.log10(max(0.1, signal_power / noise_floor_power))

        # Spectral subtraction approximation in time-domain
        noise_amplitude = np.sqrt(noise_floor_power)
        clean_signal = np.sign(signal) * np.maximum(0.0, np.abs(signal) - alpha * noise_amplitude)

        clean_power = float(np.mean(np.square(clean_signal))) + 1e-8
        filt_snr = 10.0 * np.log10(max(0.1, clean_power / noise_floor_power))
        gain = float(filt_snr - orig_snr)

        logger.info(f"Crowd Noise Spectral Filter: Orig SNR={orig_snr:.1f}dB, Clean SNR={filt_snr:.1f}dB, Gain={gain:.1f}dB")

        return clean_signal, CrowdNoiseFilterResult(
            original_snr_db=round(orig_snr, 1),
            filtered_snr_db=round(filt_snr, 1),
            noise_reduction_gain_db=round(gain, 1),
            clean_audio_samples_count=len(clean_signal)
        )
