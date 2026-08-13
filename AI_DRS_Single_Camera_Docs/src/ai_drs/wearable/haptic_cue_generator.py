"""
Haptic Feedback Vibration Cue Generator for Smart Wristbands & Watches
"""

from typing import List
from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.wearable.haptic")


class HapticImpulsePattern(BaseModel):
    """Schema representing haptic vibration pulse sequence."""
    event_type: str
    pulse_durations_ms: List[int]
    frequency_hz: int = Field(default=150)
    intensity_pct: int = Field(ge=0, le=100)


class HapticCueGenerator:
    """Encodes distinct haptic vibration patterns for smart wristbands and watches."""

    @staticmethod
    def generate_haptic_pattern(event_type: str) -> HapticImpulsePattern:
        """Generates vibration pulse sequence (1 pulse = Legal, 2 pulses = No-Ball, 3 pulses = Wicket)."""
        evt = event_type.upper()

        if evt in ("WICKET", "OUT"):
            pulses = [300, 100, 300, 100, 500]  # 3 strong pulses
            intensity = 100
        elif "NO_BALL" in evt or "NOBALL" in evt:
            pulses = [200, 100, 200]  # 2 pulses
            intensity = 80
        elif "WIDE" in evt:
            pulses = [150, 80, 150]  # 2 short pulses
            intensity = 70
        else:
            pulses = [100]  # 1 short pulse
            intensity = 40

        logger.info(f"Generated Haptic Cue [{evt}]: pulses={pulses}, intensity={intensity}%")

        return HapticImpulsePattern(
            event_type=evt,
            pulse_durations_ms=pulses,
            intensity_pct=intensity
        )
