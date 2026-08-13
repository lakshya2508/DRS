"""
Unit tests for Duckworth-Lewis-Stern (DLS 4.0) Resource Percentage Engine Module
"""

import pytest

from ai_drs.match.dls_engine import DLSEngine


def test_dls_engine_resources():
    # 50 overs, 0 wickets = 100%
    r50 = DLSEngine.get_resource_percentage(50.0, 0)
    assert r50 == 100.0

    # 20 overs, 0 wickets ~ 55-60%
    r20 = DLSEngine.get_resource_percentage(20.0, 0)
    assert 50.0 < r20 < 65.0

    # 20 overs, 5 wickets ~ 30-40%
    r20_5 = DLSEngine.get_resource_percentage(20.0, 5)
    assert 25.0 < r20_5 < 45.0
    assert r20_5 < r20

    # 0 overs = 0%
    r0 = DLSEngine.get_resource_percentage(0.0, 0)
    assert r0 == 0.0
