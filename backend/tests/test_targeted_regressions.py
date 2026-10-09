"""
ElderShield — Targeted Regression Test Suite
Validates specific bug fixes for unfamiliar payment patterns:
1. Currency prefix notation (e.g. 'rupees 350' vs '350 rupees' before account transfer).
2. Teluglish and regional utility payment commands (e.g. 'gpay cheyyandi', 'current office nunchi calling').
3. Preservation of insufficient evidence and legitimate safeguard outcomes.
"""

import pytest
from engine.analyzer import engine, parse_raw_transcript

def test_regression_currency_prefix_transfer():
    """
    Regression test for unfam_pay_009_en:
    Verifies that 'transfer rupees 350 to our clearing account' is identified
    as a FINANCIAL_TRANSFER signal even when currency word precedes the number.
    """
    transcript = (
        "Caller: BESCOM power office assistant engineer speaking.\n"
        "Senior: Good afternoon sir.\n"
        "Caller: Your power will be cut tonight at 9 PM. Transfer rupees 350 to our clearing account right now."
    )
    turns = parse_raw_transcript(transcript)
    assessment = engine.analyze(turns=turns, raw_transcript=transcript)

    assert assessment.signals_summary.financial_transfer_requests is True, (
        "Failed to identify 'transfer rupees 350 to clearing account' as financial transfer"
    )
    assert assessment.signals_summary.urgency_and_threats is True
    assert assessment.decision == "BLOCK"
    assert assessment.risk_level == "HIGH_RISK"
    assert assessment.risk_score >= 75.0

def test_regression_teluglish_utility_payment():
    """
    Regression test for unfam_pay_012_teluglish:
    Verifies that 'gpay cheyyandi' combined with utility disconnection threats
    triggers high risk scam detection.
    """
    transcript = (
        "Caller: Current office nunchi calling saar. Eeroju night current cut untundi bill kattakapothe.\n"
        "Senior: Ela kattali babu?\n"
        "Caller: Ippude gpay cheyyandi rupees 500, lekapothe 10 nimishallo power cutoff chesthamu."
    )
    turns = parse_raw_transcript(transcript)
    assessment = engine.analyze(turns=turns, raw_transcript=transcript)

    assert assessment.signals_summary.financial_transfer_requests is True, (
        "Failed to identify 'gpay cheyyandi' as financial transfer demand"
    )
    assert assessment.signals_summary.urgency_and_threats is True
    assert assessment.decision == "BLOCK"
    assert assessment.risk_level == "HIGH_RISK"
    assert assessment.risk_score >= 75.0

def test_regression_preserves_legitimate_utility_notice():
    """
    Verifies that utility discussions with standard grace periods and no coercion
    are NOT falsely flagged as scams.
    """
    transcript = (
        "Caller: Hello Sharmaji, bijli office se meter reading slip ke baare mein call hai.\n"
        "Senior: Haan kitna bill aaya is baar?\n"
        "Caller: 680 rupees ka bill bana hai sir. Due date 25 tarikh hai, aaram se online ya counter par pay kar dena."
    )
    turns = parse_raw_transcript(transcript)
    assessment = engine.analyze(turns=turns, raw_transcript=transcript)

    assert assessment.decision != "BLOCK"
    assert assessment.risk_level in ("LOW_RISK", "INSUFFICIENT_EVIDENCE")
    assert assessment.risk_score <= 25.0
