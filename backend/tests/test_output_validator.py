"""Unit tests for OutputValidator formatting and constraint enforcement."""

import pytest

from backend.app.guardrails.output_validator import OutputValidator


@pytest.fixture
def validator() -> OutputValidator:
    return OutputValidator()


def test_financial_abbreviations_sentence_splitting(validator: OutputValidator):
    """Verify that sentence tokenizer does not split on financial abbreviations."""
    sample_text = (
        "The min. SIP amount for HDFC Mid-Cap Fund is Rs. 100/- per mo. as per SEBI reg. guidelines. "
        "The TER is approx. 0.74% for Direct Plan vs. 1.65% for Regular Plan. "
        "Redemptions after 1 year carry Nil exit load."
    )
    sentences = validator.split_into_sentences(sample_text)
    assert len(sentences) == 3
    assert sentences[0].startswith("The min. SIP")
    assert sentences[1].startswith("The TER is approx.")
    assert sentences[2].startswith("Redemptions after")


def test_sentence_truncation_to_3_sentences(validator: OutputValidator):
    """Verify that responses exceeding 3 sentences are truncated to top 3."""
    long_text = (
        "Sentence one describes the fund objective. "
        "Sentence two details the expense ratio. "
        "Sentence three explains the exit load rules. "
        "Sentence four is extra and should be dropped. "
        "Sentence five is also redundant."
    )
    formatted, count = validator.validate_and_format(
        raw_text=long_text,
        canonical_url="https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
        last_updated="2024-04-01",
        max_sentences=3,
    )
    assert count == 3
    assert "Sentence four" not in formatted
    assert "Sentence five" not in formatted
    assert "Sentence one" in formatted
    assert "Sentence three" in formatted


def test_single_whitelisted_citation_enforcement(validator: OutputValidator):
    """Verify that extra/hallucinated links in raw text are stripped and replaced with 1 valid URL."""
    raw_with_links = (
        "For HDFC Small Cap Fund, visit [Groww](https://hallucinated-link.com) for details. "
        "You can also check www.investopedia.com/hdfc for exit load rules. "
        "The exit load is 1% within 365 days."
    )
    formatted, _ = validator.validate_and_format(
        raw_text=raw_with_links,
        canonical_url="https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
        last_updated="2024-04-01",
    )
    # Hallucinated URLs must be removed
    assert "https://hallucinated-link.com" not in formatted
    assert "www.investopedia.com" not in formatted
    # Exactly one canonical Source line
    assert formatted.count("Source: https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth") == 1


def test_timestamp_footer_enforcement(validator: OutputValidator):
    """Verify that the timestamp footer is consistently appended."""
    raw_text = "The lock-in period for HDFC ELSS Tax Saver Fund is 3 years from allotment date."
    formatted, count = validator.validate_and_format(
        raw_text=raw_text,
        canonical_url="https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth",
        last_updated="2024-04-01",
    )
    assert count == 1
    assert "Last updated from sources: 2024-04-01" in formatted


def test_disclaimer_attachment_when_requested(validator: OutputValidator):
    """Verify that optional compliance disclaimer is properly appended."""
    raw_text = "The exit load is 1.00% within 15 days for HDFC Gold ETF Fund of Fund."
    formatted, _ = validator.validate_and_format(
        raw_text=raw_text,
        canonical_url="https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth",
        last_updated="2024-04-01",
        requires_disclaimer=True,
        disclaimer_text="Facts-only. No investment advice.",
    )
    assert "Disclaimer: Facts-only. No investment advice." in formatted
