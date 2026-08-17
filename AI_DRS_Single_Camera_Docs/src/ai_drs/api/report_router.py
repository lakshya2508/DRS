"""
Report Router — Exportable Match Summary & DRS Review PDF/HTML Report Generator API.
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse

from ai_drs.reports.match_report_generator import MatchReportGenerator
from ai_drs.match.live_match_engine import LiveMatchEngine, CreateLiveMatchRequest

report_router = APIRouter(prefix="/api/v1/reports", tags=["Match Reports"])
_report_gen = MatchReportGenerator()
_engine = LiveMatchEngine()


@report_router.get("/generate/{match_id}", response_class=HTMLResponse)
def generate_html_report(match_id: str):
    """Generates an HTML DRS Match Summary report ready for printing or export."""
    match = _engine.get_match(match_id)
    if not match:
        # Create temporary match state for report demo if not active
        req = CreateLiveMatchRequest(league="IPL", team1_name="Mumbai Indians", team2_name="Chennai Super Kings")
        match = _engine.create_match(req)
        match.match_id = match_id

    text_report = _report_gen.generate_text_summary(match)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8"/>
<title>AI DRS Match Report — {match_id}</title>
<style>
  body {{ font-family: 'Courier New', monospace; background: #06090f; color: #00e5a0; padding: 40px; line-height: 1.5; }}
  .report-box {{ background: #0d1520; border: 1px solid rgba(0,229,160,0.3); padding: 30px; border-radius: 8px; max-width: 900px; margin: 0 auto; white-space: pre-wrap; }}
  h1 {{ font-family: sans-serif; color: #fff; text-align: center; margin-bottom: 20px; }}
  .btn-print {{ background: #00e5a0; color: #000; font-weight: bold; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; float: right; }}
</style>
</head>
<body>
  <button class="btn-print" onclick="window.print()">PRINT REPORT</button>
  <div class="report-box">
{text_report}
  </div>
</body>
</html>
"""
    return HTMLResponse(content=html_content)
