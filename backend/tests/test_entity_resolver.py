"""Unit tests for the Entity & Parameter Intent Resolver."""

import pytest

from backend.app.rag.entity_resolver import EntityResolver
from backend.app.schemas.retrieval import ParameterType, ResolutionStatus


@pytest.fixture
def resolver() -> EntityResolver:
    return EntityResolver()


def test_scheme_alias_resolution_all_5_schemes(resolver: EntityResolver):
    """Verify that all 5 curated HDFC schemes are accurately resolved from various aliases."""
    test_cases = [
        ("What is the expense ratio of HDFC Mid-Cap Opportunities Fund?", "hdfc-mid-cap-fund-direct-growth"),
        ("HDFC midcap fund exit load", "hdfc-mid-cap-fund-direct-growth"),
        ("Tell me about mid cap fund", "hdfc-mid-cap-fund-direct-growth"),
        ("What is the exit load for HDFC Small Cap Fund?", "hdfc-small-cap-fund-direct-growth"),
        ("Smallcap fund min sip", "hdfc-small-cap-fund-direct-growth"),
        ("HDFC gold etf fund of fund holding period", "hdfc-gold-etf-fund-of-fund-direct-plan-growth"),
        ("Gold fof exit load", "hdfc-gold-etf-fund-of-fund-direct-plan-growth"),
        ("What is the benchmark of HDFC Top 100 Fund?", "hdfc-large-cap-fund-direct-growth"),
        ("HDFC large cap fund expense ratio", "hdfc-large-cap-fund-direct-growth"),
        ("Top100 fund min lump sum", "hdfc-large-cap-fund-direct-growth"),
        ("What is the lock-in for HDFC ELSS Tax Saver Fund?", "hdfc-elss-tax-saver-fund-direct-plan-growth"),
        ("HDFC tax saver lockin period", "hdfc-elss-tax-saver-fund-direct-plan-growth"),
    ]

    for query, expected_code in test_cases:
        res = resolver.resolve(query)
        assert res.status == ResolutionStatus.RESOLVED, f"Failed for query: {query}"
        assert res.scheme_code == expected_code, f"Expected {expected_code}, got {res.scheme_code} for query: {query}"


def test_parameter_detection(resolver: EntityResolver):
    """Verify that parameter intents are properly classified across all domains."""
    test_cases = [
        ("What is the TER of HDFC Mid Cap?", ParameterType.EXPENSE_RATIO, "expense_ratio"),
        ("What is the exit load of HDFC Small Cap?", ParameterType.EXIT_LOAD, "exit_load"),
        ("What is the minimum SIP amount for HDFC Top 100?", ParameterType.INVESTMENT_LIMITS, "investment_limits"),
        ("What is the minimum lump sum for HDFC Mid Cap?", ParameterType.INVESTMENT_LIMITS, "investment_limits"),
        ("Is there a 3-year lock-in for HDFC ELSS?", ParameterType.LOCK_IN_PERIOD, "lock_in_period"),
        ("What are the capital gains tax rules for HDFC Gold FoF?", ParameterType.TAXATION, "taxation"),
        ("What is the riskometer rating of HDFC Small Cap?", ParameterType.FUND_OVERVIEW, "fund_overview"),
        ("What is the benchmark index of HDFC Large Cap?", ParameterType.FUND_OVERVIEW, "fund_overview"),
    ]

    for query, expected_type, expected_str in test_cases:
        res = resolver.resolve(query)
        assert res.parameter_type == expected_type, f"Expected {expected_type} for query: {query}"
        assert res.parameter == expected_str, f"Expected {expected_str} for query: {query}"


def test_ambiguous_scheme_interception_ec01(resolver: EntityResolver):
    """Verify that parameter queries lacking any scheme name trigger AMBIGUOUS_SCHEME (EC-01)."""
    ambiguous_queries = [
        "What is the exit load?",
        "What is the minimum SIP amount?",
        "What is the lock-in period?",
        "What is the total expense ratio?",
        "How much is the lump sum investment?",
        "What is the riskometer rating?",
    ]

    for query in ambiguous_queries:
        res = resolver.resolve(query)
        assert res.status == ResolutionStatus.AMBIGUOUS_SCHEME, f"Expected AMBIGUOUS_SCHEME for: {query}"
        assert res.is_ambiguous is True


def test_out_of_scope_scheme_interception_ec02(resolver: EntityResolver):
    """Verify that queries for competitor AMCs or unsupported schemes trigger OUT_OF_SCOPE (EC-02)."""
    out_of_scope_queries = [
        ("What is the expense ratio of SBI Bluechip Fund?", "Sbi"),
        ("What is the exit load of ICICI Prudential Liquid Fund?", "Icici"),
        ("Tell me about Axis Small Cap Fund", "Axis"),
        ("What is the TER of Parag Parikh Flexi Cap Fund?", "Parag Parikh"),
        ("What is the NAV of Tata Digital India Fund?", "Tata"),
        ("What is the TER of HDFC Balanced Advantage Fund?", "Hdfc Balanced Advantage"),
        ("Tell me about HDFC Flexi Cap Fund", "Hdfc Flexi Cap"),
    ]

    for query, expected_out in out_of_scope_queries:
        res = resolver.resolve(query)
        assert res.status == ResolutionStatus.OUT_OF_SCOPE, f"Expected OUT_OF_SCOPE for: {query}"
        assert res.out_of_scope_name is not None
        assert expected_out.lower() in res.out_of_scope_name.lower()


def test_general_operations_queries(resolver: EntityResolver):
    """Verify that statement and capital gains report queries resolve to general operations."""
    ops_queries = [
        "How to download my mutual fund account statement?",
        "Where can I get my capital gains report for ITR filing?",
        "How to download schedule 112a tax statement?",
    ]

    for query in ops_queries:
        res = resolver.resolve(query)
        assert res.status == ResolutionStatus.GENERAL_OPERATIONS, f"Expected GENERAL_OPERATIONS for: {query}"
        assert res.scheme_code == "general-operations"


def test_hinglish_and_typo_queries_ec12(resolver: EntityResolver):
    """Verify phonetic and spelling variations resolve accurately (EC-12)."""
    typo_queries = [
        ("HDFC elss tax sevar ka lockin kitna h?", "hdfc-elss-tax-saver-fund-direct-plan-growth"),
        ("HDFC midcap fund ka expense ratio kya hai", "hdfc-mid-cap-fund-direct-growth"),
        ("gold fof ka exit load", "hdfc-gold-etf-fund-of-fund-direct-plan-growth"),
    ]

    for query, expected_code in typo_queries:
        res = resolver.resolve(query)
        assert res.scheme_code == expected_code, f"Failed resolving typo query: {query}"
