"""
Unit tests for Automated Match Report HTML/PDF Exporter Module
"""

import pytest

from ai_drs.evaluation.pdf_exporter import MatchReportCard, MatchReportExporter
from ai_drs.match.models import MatchState, TossState


def test_match_report_exporter():
    match_state = MatchState(
        match_id="M_REPORT_101",
        team_a="India",
        team_b="Australia",
        runs=185,
        wickets=4,
        overs=19,
        legal_balls=3
    )

    toss_state = TossState(
        toss_winner="India",
        toss_choice="BAT",
        batting_team="India",
        bowling_team="Australia"
    )


    card = MatchReportExporter.generate_html_report(match_state, toss_state)

    assert isinstance(card, MatchReportCard)
    assert card.match_id == "M_REPORT_101"
    assert "India won the toss" in card.toss_summary
    assert "Australia: 185/4" in card.scorecard_summary
    assert "<!DOCTYPE html>" in card.html_content
