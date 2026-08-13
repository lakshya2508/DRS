"""
Unit tests for PDF Match Summary Executive Exporter Module
"""

from pathlib import Path
import pytest

from ai_drs.evaluation.pdf_summary_exporter import ExecutivePDFSummaryResult, PDFSummaryExporter
from ai_drs.match.models import MatchState


def test_pdf_summary_exporter(tmp_path: Path):
    pdf_path = str(tmp_path / "executive_summary.pdf")
    match_state = MatchState(match_id="M_EXEC_01", runs=210, wickets=5, overs=20, legal_balls=0)

    res = PDFSummaryExporter.export_executive_summary_pdf(match_state, pdf_path)

    assert isinstance(res, ExecutivePDFSummaryResult)
    assert res.match_id == "M_EXEC_01"
    assert res.is_generated is True
    assert Path(pdf_path).exists()
