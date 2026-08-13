"""
Live Stadium Decibel Level & Atmosphere Meter Module
"""

import numpy as np
from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.audio.decibel")


class StadiumAtmosphereMetrics(BaseModel):
    """Schema representing stadium acoustic sound pressure level (dB SPL) and excitement state."""
    spl_decibels_db: float = Field(ge=0.0, le=140.0)
    atmosphere_state: str = Field(description="'QUIET', 'NORMAL', 'LOUD', 'ECSTATIC_ROAR'")
    is_excitement_spike: bool


class StadiumDecibelMeterEngine:
    """Measures real-time stadium crowd decibel sound pressure levels (dB SPL) and detects crowd excitement spikes."""

    @staticmethod
    def measure_stadium_decibels(audio_chunk: np.ndarray, reference_pressure: float = 2e-5) -> StadiumAtmosphereMetrics:
        """Calculates sound pressure level in dB SPL from raw audio pressure samples."""
        if audio_chunk is None or len(audio_chunk) == 0:
            return StadiumAtmosphereMetrics(spl_decibels_db=40.0, atmosphere_state="QUIET", is_excitement_spike=False)

        rms_pressure = float(np.sqrt(np.mean(np.square(audio_chunk.astype(np.float32)))))
        if rms_pressure <= 0.0:
            db_spl = 40.0
        else:
            db_spl = float(20.0 * np.log10(rms_pressure / reference_pressure))
            db_spl = min(135.0, max(30.0, db_spl))

        if db_spl >= 105.0:
            state = "ECSTATIC_ROAR"
            spike = True
        elif db_spl >= 85.0:
            state = "LOUD"
            spike = False
        elif db_spl >= 65.0:
            state = "NORMAL"
            spike = False
        else:
            state = "QUIET"
            spike = False

        logger.debug(f"Stadium Decibel Meter: SPL={db_spl:.1f} dB, State={state}, Spike={spike}")

        return StadiumAtmosphereMetrics(
            spl_decibels_db=round(db_spl, 1),
            atmosphere_state=state,
            is_excitement_spike=spike
        )
