"""
Unit tests for MCC Law 36 & ICC DRS Appendix 1 Rule Compliance Verifier Module
"""

import pytest

from ai_drs.evaluation.icc_rulebook_verifier import ICCRulebookVerifier, RuleComplianceResult


def test_icc_rulebook_verifier():
    res = ICCRulebookVerifier.verify_drs_decision_rules(pitch_x_m=0.0, impact_x_m=0.0, wicket_x_m=0.05)

    assert isinstance(res, RuleComplianceResult)
    assert res.mcc_law_36_compliant is True
    assert res.icc_appendix_1_compliant is True
    assert res.umpires_call_margin_mm == 36.0
    assert res.verification_status == "100% COMPLIANT"
