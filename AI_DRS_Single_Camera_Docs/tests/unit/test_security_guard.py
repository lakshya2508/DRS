"""
Unit tests for Enterprise System Security Audit & Rate Limiting Guard Module
"""

import pytest

from ai_drs.enterprise.security_guard import SecurityAuditReport, SecurityGuardEngine


def test_security_guard_normal():
    guard = SecurityGuardEngine(max_requests_per_min=10)
    rep = guard.validate_request("192.168.1.50")

    assert isinstance(rep, SecurityAuditReport)
    assert rep.client_ip == "192.168.1.50"
    assert rep.is_rate_limited is False
    assert rep.security_status == "🛡️ SECURE"


def test_security_guard_rate_limit():
    guard = SecurityGuardEngine(max_requests_per_min=2)
    guard.validate_request("10.0.0.1")
    guard.validate_request("10.0.0.1")
    rep = guard.validate_request("10.0.0.1")

    assert rep.is_rate_limited is True
    assert rep.security_status == "⛔ RATE LIMITED"
