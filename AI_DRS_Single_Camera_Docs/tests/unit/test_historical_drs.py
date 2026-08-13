"""
Unit tests for Historical Famous DRS Controversies Replay Suite Module
"""

import pytest

from ai_drs.evaluation.historical_drs_benchmarks import (
    HistoricalDRSBenchmarkResult,
    HistoricalDRSSuiteRunner,
)


def test_historical_drs_benchmarks():
    results = HistoricalDRSSuiteRunner.run_historical_benchmarks()

    assert len(results) == 2
    assert all(isinstance(r, HistoricalDRSBenchmarkResult) for r in results)
    assert all(r.decision_matches_official is True for r in results)
    assert any(r.controversy_id == "HIST_TENDULKAR_2011" for r in results)
