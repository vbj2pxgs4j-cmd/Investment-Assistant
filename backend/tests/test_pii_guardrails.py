"""Unit tests for PIIFilter and data sanitization guardrails."""

import pytest

from backend.app.guardrails.pii_filter import PIIFilter
from backend.app.schemas.guardrails import PIIType


@pytest.fixture
def pii_filter() -> PIIFilter:
    return PIIFilter()


def test_standard_pan_detection(pii_filter: PIIFilter):
    """Verify that standard PAN patterns are detected and masked."""
    queries = [
        "My PAN is ABCDE1234F, what is my folio status?",
        "PAN: BKZPA9876Q for HDFC Tax Saver",
    ]

    for q in queries:
        result = pii_filter.check(q)
        assert result.is_pii_detected is True
        assert PIIType.PAN in result.detected_types
        assert "[REDACTED_PAN]" in result.masked_query
        assert result.security_message is not None


def test_obfuscated_and_spaced_pan_detection_ec07(pii_filter: PIIFilter):
    """Verify that obfuscated, spaced, and hyphenated PANs are caught (EC-07)."""
    obfuscated_queries = [
        "My PAN number is A B C D E 1 2 3 4 F check my account",
        "PAN is A-B-C-D-E-1-2-3-4-F please verify",
        "Here is my pan a.b.c.d.e.1.2.3.4.f",
    ]

    for q in obfuscated_queries:
        result = pii_filter.check(q)
        assert result.is_pii_detected is True
        assert PIIType.PAN in result.detected_types
        assert result.security_message is not None


def test_aadhaar_number_detection(pii_filter: PIIFilter):
    """Verify that 12-digit Aadhaar formats are detected."""
    queries = [
        "My Aadhaar is 2345 6789 0123 link to folio",
        "Aadhaar: 3456-7890-1234",
    ]

    for q in queries:
        result = pii_filter.check(q)
        assert result.is_pii_detected is True
        assert PIIType.AADHAAR in result.detected_types
        assert result.security_message is not None


def test_mobile_number_detection(pii_filter: PIIFilter):
    """Verify that Indian phone numbers are detected."""
    queries = [
        "Call me on +91 9876543210 regarding my SIP",
        "My contact number is 8765432109",
    ]

    for q in queries:
        result = pii_filter.check(q)
        assert result.is_pii_detected is True
        assert PIIType.PHONE in result.detected_types


def test_email_address_detection(pii_filter: PIIFilter):
    """Verify that email addresses are detected and masked."""
    q = "Send statement to investor.help@gmail.com please"
    result = pii_filter.check(q)
    assert result.is_pii_detected is True
    assert PIIType.EMAIL in result.detected_types
    assert "[REDACTED_EMAIL]" in result.masked_query


def test_otp_code_detection(pii_filter: PIIFilter):
    """Verify that authentication OTP codes are detected."""
    queries = [
        "My OTP is 492018 for redemption",
        "Verification code: 123456",
    ]

    for q in queries:
        result = pii_filter.check(q)
        assert result.is_pii_detected is True
        assert PIIType.OTP in result.detected_types


def test_clean_queries_pass_cleanly(pii_filter: PIIFilter):
    """Verify that normal factual mutual fund queries pass without PII triggers."""
    clean_queries = [
        "What is the exit load for HDFC Small Cap Fund?",
        "What is the TER of HDFC Mid-Cap Opportunities Fund?",
        "Is there a 3-year lock-in period for HDFC ELSS?",
        "What is the minimum SIP amount for HDFC Top 100?",
        "How to download capital gains statement on Groww?",
    ]

    for q in clean_queries:
        result = pii_filter.check(q)
        assert result.is_pii_detected is False
        assert len(result.detected_types) == 0
        assert result.masked_query == q
