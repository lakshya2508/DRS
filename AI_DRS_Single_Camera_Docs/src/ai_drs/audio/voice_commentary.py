"""
AI Match Commentary Voice Generator Module for Play-by-Play Audio
"""

from typing import List
from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger
from ai_drs.match.models import DeliveryEvent

logger = setup_logger("ai_drs.audio.commentary")


class CommentaryAudioScript(BaseModel):
    """Schema representing generated live match commentary audio transcript."""
    delivery_id: str
    ball_number_str: str
    commentary_text: str
    excitement_level: str = Field(description="'HIGH', 'MEDIUM', 'NORMAL'")


class VoiceCommentaryGenerator:
    """Generates energetic, professional play-by-play voice commentary scripts for delivery events."""

    @staticmethod
    def generate_delivery_commentary(delivery: DeliveryEvent, batter_name: str = "Batter", bowler_name: str = "Bowler") -> CommentaryAudioScript:
        """Generates dynamic match commentary script based on ball outcome."""
        ball_str = f"{delivery.over_number}.{delivery.ball_number}"

        if delivery.is_wicket:
            text = f"OUT! {bowler_name} strikes! {batter_name} is dismissed ({delivery.dismissal_type or 'Out'})! What a massive breakthrough!"
            level = "HIGH"
        elif delivery.runs_batter == 6:
            text = f"SIX! Magnificent shot by {batter_name}! High, handsome, and straight into the crowd!"
            level = "HIGH"
        elif delivery.runs_batter == 4:
            text = f"FOUR! Beautifully struck by {batter_name}! Crinkled past the fielder to the fence!"
            level = "MEDIUM"
        elif delivery.runs_batter == 0:
            text = f"{bowler_name} to {batter_name}, dot ball. Well defended outside off stump."
            level = "NORMAL"
        else:
            text = f"{bowler_name} to {batter_name}, {delivery.runs_batter} run(s) taken cleanly."
            level = "NORMAL"

        logger.info(f"Generated Live Commentary [{ball_str}]: {text}")

        return CommentaryAudioScript(
            delivery_id=f"del_{ball_str}",
            ball_number_str=ball_str,
            commentary_text=text,
            excitement_level=level
        )
