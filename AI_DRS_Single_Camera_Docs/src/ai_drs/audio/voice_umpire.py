"""
Autonomous Third Umpire Voice Assistant & Official Callout Generator
"""

from typing import List
from pydantic import BaseModel, Field

from ai_drs.api.review_service import ReviewResultResponse
from ai_drs.common.logging import setup_logger

logger = setup_logger("ai_drs.audio.voice_umpire")


class VoiceUmpireCallout(BaseModel):
    """Schema representing TV third umpire official voice callout transcript."""
    review_id: str
    callout_transcript: str
    spoken_steps: List[str]
    final_voice_command: str


class VoiceUmpireAssistant:
    """Generates official TV broadcast TV third umpire voice callout transcripts."""

    @staticmethod
    def generate_drs_voice_callout(review: ReviewResultResponse) -> VoiceUmpireCallout:
        """Generates TV third umpire step-by-step audio commentary transcript."""
        ev = review.evidence

        p_str = f"Pitching {ev.pitching_zone.value.replace('_', ' ').lower()}"
        i_str = f"Impact {ev.impact_zone.value.replace('_', ' ').lower()}"
        w_str = f"Wickets {ev.hit_stumps_status.value.lower()}"

        steps = [
            "We are ready for the decision review.",
            f"Checking pitching... {p_str.capitalize()}.",
            f"Checking impact... {i_str.capitalize()}.",
            f"Checking wickets projection... {w_str.capitalize()}."
        ]

        if review.decision.value == "OUT":
            cmd = "Please stay with your on-field decision OUT. Signal OUT now."
        elif review.decision.value == "NOT OUT":
            cmd = "I recommend reversing your decision to NOT OUT. Signal NOT OUT now."
        else:
            cmd = "Evidence is INCONCLUSIVE due to low tracking confidence. Stay with on-field decision."

        steps.append(cmd)
        transcript = " ".join(steps)

        logger.info(f"Generated Autonomous Third Umpire Voice Callout [{review.review_id}]: {cmd}")

        return VoiceUmpireCallout(
            review_id=review.review_id,
            callout_transcript=transcript,
            spoken_steps=steps,
            final_voice_command=cmd
        )
