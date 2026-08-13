"""
Acoustic Calibration & Snicko Threshold Auto-Tuner Module
"""

from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.audio.snicko_autotuner")


class SnickoAutoTunerConfig(BaseModel):
    """Schema representing dynamic Snicko threshold calibration config."""
    background_decibels_db: float
    base_peak_threshold_ratio: float
    tuned_peak_threshold_ratio: float
    noise_environment: str = Field(description="'QUIET_GROUND', 'MEDIUM_STADIUM', 'LOUD_STADIUM'")


class SnickoAutoTunerEngine:
    """Dynamically auto-tunes Snicko spike detection threshold ratios based on background decibel levels."""

    @staticmethod
    def tune_snicko_threshold(background_db_spl: float = 75.0, base_ratio: float = 3.5) -> SnickoAutoTunerConfig:
        """Adjusts Snicko spike threshold ratio up in loud environments to prevent false edge triggers."""
        if background_db_spl >= 95.0:
            env = "LOUD_STADIUM"
            tuned_ratio = float(base_ratio * 1.5)  # Raise threshold by 50%
        elif background_db_spl >= 75.0:
            env = "MEDIUM_STADIUM"
            tuned_ratio = float(base_ratio * 1.2)  # Raise threshold by 20%
        else:
            env = "QUIET_GROUND"
            tuned_ratio = float(base_ratio)

        logger.info(f"Auto-Tuned Snicko Threshold [{env}]: {background_db_spl:.1f}dB -> Ratio={tuned_ratio:.2f} (Base={base_ratio})")

        return SnickoAutoTunerConfig(
            background_decibels_db=background_db_spl,
            base_peak_threshold_ratio=base_ratio,
            tuned_peak_threshold_ratio=round(tuned_ratio, 2),
            noise_environment=env
        )
