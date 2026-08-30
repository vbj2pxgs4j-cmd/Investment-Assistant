"""Integration and precision tests for SchemeFilteredRetriever.

Verifies zero cross-scheme collisions, high precision across all 5 schemes,
canonical source attribution, and ambiguity / out-of-scope handling.
"""

import pytest

from backend.app.rag.retriever import SchemeFilteredRetriever
from backend.app.rag.vector_store import VectorStoreService
from backend.app.schemas.retrieval import ParameterType, ResolutionStatus


@pytest.fixture(scope="module")
def retriever() -> SchemeFilteredRetriever:
    vector_store = VectorStoreService()
    vector_store.initialize_store(force_reload=False)
    return SchemeFilteredRetriever(vector_store=vector_store)


def test_zero_cross_scheme_collision_exit_loads(retriever: SchemeFilteredRetriever):
    """Verify that exit load queries for each scheme retrieve the exact correct scheme chunk."""
    # Mid Cap: 1% within 1 year
    mid_res = retriever.retrieve("What is the exit load of HDFC Mid-Cap Opportunities Fund?")
    assert mid_res.status == ResolutionStatus.RESOLVED
    assert mid_res.primary_chunk is not None
    assert mid_res.primary_chunk.scheme_code == "hdfc-mid-cap-fund-direct-growth"
    assert "1.00%" in mid_res.primary_chunk.content or "1%" in mid_res.primary_chunk.content
    assert "1 year" in mid_res.primary_chunk.content or "365 days" in mid_res.primary_chunk.content
    assert mid_res.official_source_url == "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth"

    # Small Cap: 1% within 1 year
    small_res = retriever.retrieve("What is the exit load for HDFC Small Cap Fund?")
    assert small_res.status == ResolutionStatus.RESOLVED
    assert small_res.primary_chunk is not None
    assert small_res.primary_chunk.scheme_code == "hdfc-small-cap-fund-direct-growth"
    assert "1.00%" in small_res.primary_chunk.content or "1%" in small_res.primary_chunk.content
    assert small_res.official_source_url == "https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth"

    # Gold FoF: 1% within 15 days
    gold_res = retriever.retrieve("What is the exit load of HDFC Gold ETF Fund of Fund?")
    assert gold_res.status == ResolutionStatus.RESOLVED
    assert gold_res.primary_chunk is not None
    assert gold_res.primary_chunk.scheme_code == "hdfc-gold-etf-fund-of-fund-direct-plan-growth"
    assert "15 days" in gold_res.primary_chunk.content
    assert gold_res.official_source_url == "https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth"

    # ELSS: Nil / No exit load
    elss_res = retriever.retrieve("What is the exit load for HDFC ELSS Tax Saver Fund?")
    assert elss_res.status == ResolutionStatus.RESOLVED
    assert elss_res.primary_chunk is not None
    assert elss_res.primary_chunk.scheme_code == "hdfc-elss-tax-saver-fund-direct-plan-growth"
    assert "Nil" in elss_res.primary_chunk.content or "no exit load" in elss_res.primary_chunk.content.lower()
    assert elss_res.official_source_url == "https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth"


def test_zero_cross_scheme_collision_lock_in_periods(retriever: SchemeFilteredRetriever):
    """Verify that ELSS returns 3-year lock-in while open-ended funds return Nil lock-in."""
    # ELSS Fund
    elss_res = retriever.retrieve("What is the lock-in period for HDFC ELSS Tax Saver Fund?")
    assert elss_res.status == ResolutionStatus.RESOLVED
    assert elss_res.primary_chunk is not None
    assert elss_res.primary_chunk.scheme_code == "hdfc-elss-tax-saver-fund-direct-plan-growth"
    assert "3-year" in elss_res.primary_chunk.content or "3 years" in elss_res.primary_chunk.content

    # Mid Cap Fund (Open-ended, No lock-in)
    mid_res = retriever.retrieve("Is there any lock in for HDFC Mid Cap Fund?")
    assert mid_res.status == ResolutionStatus.RESOLVED
    assert mid_res.primary_chunk is not None
    assert mid_res.primary_chunk.scheme_code == "hdfc-mid-cap-fund-direct-growth"
    assert "No lock-in" in mid_res.primary_chunk.content or "Nil" in mid_res.primary_chunk.content


def test_zero_cross_scheme_collision_expense_ratios(retriever: SchemeFilteredRetriever):
    """Verify that TER queries retrieve exact figures for each respective fund."""
    # Mid Cap: ~0.74%
    mid_res = retriever.retrieve("What is the TER of HDFC Mid Cap Fund?")
    assert mid_res.primary_chunk.scheme_code == "hdfc-mid-cap-fund-direct-growth"
    assert "0.74%" in mid_res.primary_chunk.content

    # Top 100: ~1.08%
    top_res = retriever.retrieve("What is the expense ratio of HDFC Top 100 Fund?")
    assert top_res.primary_chunk.scheme_code == "hdfc-large-cap-fund-direct-growth"
    assert "1.08%" in top_res.primary_chunk.content


def test_zero_cross_scheme_collision_investment_limits(retriever: SchemeFilteredRetriever):
    """Verify minimum SIP limits per scheme (e.g. ₹100 vs ₹500)."""
    # Mid Cap: min SIP ₹100
    mid_res = retriever.retrieve("What is the minimum SIP amount for HDFC Mid Cap?")
    assert "₹100" in mid_res.primary_chunk.content or "100" in mid_res.primary_chunk.content

    # ELSS: min SIP ₹500
    elss_res = retriever.retrieve("What is the minimum SIP for HDFC ELSS Tax Saver?")
    assert "₹500" in elss_res.primary_chunk.content or "500" in elss_res.primary_chunk.content


def test_ambiguous_scheme_handling(retriever: SchemeFilteredRetriever):
    """Verify that ambiguous queries return list of 5 supported schemes without guessing."""
    res = retriever.retrieve("What is the exit load?")
    assert res.status == ResolutionStatus.AMBIGUOUS_SCHEME
    assert res.primary_chunk is None
    assert len(res.supported_schemes) == 5
    assert res.ambiguity_message is not None
    assert "specify which of the 5" in res.ambiguity_message


def test_out_of_scope_handling(retriever: SchemeFilteredRetriever):
    """Verify that queries for unsupported funds return OUT_OF_SCOPE with Groww link."""
    res = retriever.retrieve("What is the expense ratio of SBI Bluechip Fund?")
    assert res.status == ResolutionStatus.OUT_OF_SCOPE
    assert res.primary_chunk is None
    assert res.out_of_scope_message is not None
    assert "Sbi" in res.out_of_scope_message
    assert res.official_source_url == "https://groww.in/mutual-funds"


def test_general_operations_retrieval(retriever: SchemeFilteredRetriever):
    """Verify retrieval of general statement download instructions."""
    res = retriever.retrieve("How to download mutual fund account statement on Groww?")
    assert res.status == ResolutionStatus.GENERAL_OPERATIONS
    assert res.primary_chunk is not None
    assert res.primary_chunk.scheme_code == "general-operations"
    assert "statement" in res.primary_chunk.content.lower()


def test_retrieval_performance_and_metadata(retriever: SchemeFilteredRetriever):
    """Verify that retrieval results include valid canonical URL, date, and latency."""
    res = retriever.retrieve("What is the riskometer rating of HDFC Small Cap Fund?")
    assert res.latency_ms > 0
    assert res.last_updated is not None and len(res.last_updated) == 10
    assert res.official_source_url.startswith("https://groww.in/mutual-funds/")
