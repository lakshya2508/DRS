"""
Automated Press Release & Social Media Copy Generator
"""

from typing import List
from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger
from ai_drs.match.models import MatchState

logger = setup_logger("ai_drs.analytics.press_release")


class PressReleaseKit(BaseModel):
    """Schema representing generated media press release kit and social media posts."""
    headline: str
    official_press_release_body: str
    twitter_thread_posts: List[str]
    hashtags: List[str]


class PressReleaseGenerator:
    """Drafts post-match official press releases, Twitter/X threads, and social media copy."""

    @staticmethod
    def generate_press_kit(match_state: MatchState, player_of_match: str = "V. Kohli") -> PressReleaseKit:
        """Generates post-match media headlines, press release body, and Twitter thread."""
        headline = f"MATCH REPORT: {match_state.team_b} Secure Thrilling Victory Over {match_state.team_a}"

        body = (
            f"FOR IMMEDIATE RELEASE\n\n"
            f"CITY — In an exhilarating contest, {match_state.team_b} posted {match_state.runs}/{match_state.wickets} "
            f"in {match_state.overs}.{match_state.legal_balls} overs to seal a memorable win against {match_state.team_a}. "
            f"Outstanding performance by Player of the Match {player_of_match} anchored the team's victory."
        )

        tweets = [
            f"🚨 RESULT: {match_state.team_b} win! Final Score: {match_state.runs}/{match_state.wickets} ({match_state.overs}.{match_state.legal_balls} ov) #Cricket #AIDRS",
            f"⭐ Player of the Match: {player_of_match} for a stellar performance! 🏏💥",
            f"📊 Check out full 3D DRS review trajectory graphics and match analytics at aidrs.io/match/{match_state.match_id}"
        ]

        hashtags = ["#Cricket", "#AIDRS", "#T20Match", "#GodModeEngine"]

        logger.info(f"Generated Media Press Release Kit [{match_state.match_id}]: '{headline}'")

        return PressReleaseKit(
            headline=headline,
            official_press_release_body=body,
            twitter_thread_posts=tweets,
            hashtags=hashtags
        )
