"""
Toss Engine Module for AI DRS (Cryptographic Coin Toss & Innings Setup)
"""

import secrets
from typing import Optional
from ai_drs.common.logging import setup_logger
from ai_drs.match.models import TossState

logger = setup_logger("ai_drs.match.toss")


class TossEngine:
    """Handles official match toss execution using cryptographic randomness."""

    @staticmethod
    def conduct_toss(
        team_a: str,
        team_b: str,
        caller_team: str,
        caller_call: str = "HEADS",
        winner_decision: Optional[str] = None
    ) -> TossState:
        """Flips coin and determines toss winner, toss decision, and batting/bowling team assignments."""
        if caller_team not in (team_a, team_b):
            raise ValueError(f"Caller team '{caller_team}' must be either '{team_a}' or '{team_b}'.")

        call = caller_call.upper()
        if call not in ("HEADS", "TAILS"):
            raise ValueError(f"Invalid coin call '{caller_call}'. Must be 'HEADS' or 'TAILS'.")

        # Cryptographically secure random coin flip
        flip_outcome = secrets.choice(["HEADS", "TAILS"])

        if flip_outcome == call:
            toss_winner = caller_team
        else:
            toss_winner = team_b if caller_team == team_a else team_a

        # If decision not provided, toss winner randomly chooses BAT (60%) or BOWL (40%)
        if winner_decision is None:
            decision = secrets.choice(["BAT", "BAT", "BAT", "BOWL", "BOWL"])
        else:
            decision = winner_decision.upper()
            if decision not in ("BAT", "BOWL"):
                raise ValueError(f"Invalid decision '{winner_decision}'. Must be 'BAT' or 'BOWL'.")

        non_winner = team_b if toss_winner == team_a else team_a

        if decision == "BAT":
            batting_team = toss_winner
            bowling_team = non_winner
        else:
            batting_team = non_winner
            bowling_team = toss_winner

        logger.info(
            f"Toss Conducted: Flip={flip_outcome}, Winner={toss_winner}, "
            f"Decision={decision}, Batting={batting_team}, Bowling={bowling_team}"
        )

        return TossState(
            toss_winner=toss_winner,
            toss_choice=decision,
            batting_team=batting_team,
            bowling_team=bowling_team
        )
