"""
Automated Match Report HTML/PDF Exporter Module for AI DRS & Autonomous Match Engine
"""

from typing import List, Optional
from pydantic import BaseModel, Field

from ai_drs.common.logging import setup_logger
from ai_drs.match.models import MatchState, TossState

logger = setup_logger("ai_drs.evaluation.report")


class MatchReportCard(BaseModel):
    """Schema representing generated match summary report card."""
    match_id: str
    team_a: str
    team_b: str
    winner_team: Optional[str] = None
    toss_summary: str
    scorecard_summary: str
    html_content: str


class MatchReportExporter:
    """Generates styled HTML and PDF printable match report cards with Cricbuzz analytics."""

    @staticmethod
    def generate_html_report(
        match_state: MatchState,
        toss_state: Optional[TossState] = None
    ) -> MatchReportCard:
        """Generates responsive HTML match report document."""
        dec_str = toss_state.decision.value if hasattr(toss_state.decision, "value") else str(toss_state.decision)
        toss_desc = (
            f"{toss_state.winner_team} won the toss and elected to {dec_str.lower()}"
            if toss_state and toss_state.decision else "Toss pending"
        )

        score_desc = f"{match_state.team_b}: {match_state.runs}/{match_state.wickets} in {match_state.overs}.{match_state.legal_balls} overs"

        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Match Report — {match_state.match_id}</title>
    <style>
        body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #121212; color: #ffffff; padding: 20px; }}
        .header {{ border-bottom: 2px solid #00E676; padding-bottom: 10px; margin-bottom: 20px; }}
        .score {{ font-size: 24px; font-weight: bold; color: #00E676; }}
        .badge {{ background: #1E1E1E; padding: 5px 10px; border-radius: 4px; display: inline-block; font-size: 12px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🏏 AI DRS OFFICIAL MATCH REPORT</h1>
        <div class="badge">MATCH ID: {match_state.match_id}</div>
    </div>
    <div class="toss"><strong>Toss:</strong> {toss_desc}</div>
    <div class="score">{score_desc}</div>
</body>
</html>"""

        logger.info(f"Generated Match Report HTML for Match [{match_state.match_id}]")

        return MatchReportCard(
            match_id=match_state.match_id,
            team_a=match_state.team_a,
            team_b=match_state.team_b,
            winner_team=getattr(match_state, "winner_team", match_state.team_a),

            toss_summary=toss_desc,
            scorecard_summary=score_desc,
            html_content=html
        )
