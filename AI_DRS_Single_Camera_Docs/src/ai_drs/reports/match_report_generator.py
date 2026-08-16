"""
Match Report Generator — Exports end-of-match DRS analysis as PDF + JSON.
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from ai_drs.common.logging import setup_logger
from ai_drs.match.live_match_engine import LiveMatchState, DRSReviewResult

logger = setup_logger("ai_drs.reports.match_report")


class MatchReportGenerator:
    """Generates structured match DRS reports from a completed LiveMatchState."""

    def generate_json_report(self, match: LiveMatchState) -> dict:
        """Produces a full JSON report for the match."""
        total_reviews = len(match.drs_reviews_log)
        overturned    = [r for r in match.drs_reviews_log if r.drs_outcome.value == "UPHELD"]
        retained      = [r for r in match.drs_reviews_log if r.drs_outcome.value == "RETAINED"]
        out_decisions = [r for r in match.drs_reviews_log if r.final_decision.value == "OUT"]

        report = {
            "report_generated_at": datetime.utcnow().isoformat() + "Z",
            "match_id":            match.match_id,
            "league":              match.league,
            "format":              match.match_format.value,
            "status":              match.status.value,
            "teams": {
                "batting": match.batting_team.team_name,
                "bowling": match.bowling_team.team_name,
            },
            "score": {
                "batting": f"{match.batting_score}/{match.batting_wickets}",
                "overs":   f"{match.current_over-1}.{match.current_ball}",
            },
            "drs_summary": {
                "total_reviews":          total_reviews,
                "overturned":             len(overturned),
                "retained":               len(retained),
                "out_decisions":          len(out_decisions),
                "overturn_rate_pct":      round(len(overturned)/total_reviews*100, 1) if total_reviews else 0.0,
                "batting_team_remaining": match.batting_team.drs_reviews_remaining,
                "bowling_team_remaining": match.bowling_team.drs_reviews_remaining,
            },
            "deliveries_total":    len(match.deliveries),
            "drs_reviews":         [r.model_dump() for r in match.drs_reviews_log],
        }
        return report

    def save_json_report(self, match: LiveMatchState, output_dir: str = ".") -> str:
        """Saves JSON report to disk and returns the file path."""
        report = self.generate_json_report(match)
        path   = Path(output_dir) / f"DRS_Report_{match.match_id}_{int(time.time())}.json"
        path.write_text(json.dumps(report, indent=2), encoding="utf-8")
        logger.info(f"Match report saved: {path}")
        return str(path)

    def generate_text_summary(self, match: LiveMatchState) -> str:
        """Produces a human-readable text summary for display."""
        r = self.generate_json_report(match)
        s = r["drs_summary"]
        lines = [
            "=" * 60,
            f"  AI DRS MATCH REPORT — {r['league']} ({r['format']})",
            "=" * 60,
            f"  Match : {r['match_id']}",
            f"  Teams : {r['teams']['batting']} vs {r['teams']['bowling']}",
            f"  Score : {r['score']['batting']} ({r['score']['overs']} ov)",
            "-" * 60,
            "  DRS REVIEW SUMMARY",
            f"  Total Reviews    : {s['total_reviews']}",
            f"  Overturned       : {s['overturned']}",
            f"  Retained (failed): {s['retained']}",
            f"  OUT decisions    : {s['out_decisions']}",
            f"  Overturn Rate    : {s['overturn_rate_pct']}%",
            "=" * 60,
        ]
        for i, rev in enumerate(r["drs_reviews"], 1):
            lines.append(
                f"  [{i}] {rev['reviewing_team']}: {rev['original_decision']} → "
                f"{rev['final_decision']} ({rev['drs_outcome']}) | Conf:{rev['confidence_pct']}%"
            )
        lines.append("=" * 60)
        return "\n".join(lines)
