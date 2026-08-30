"""Unit tests for corpus parser and schema validation."""

import json
from pathlib import Path
import pytest

from backend.app.core.config import PROJECT_ROOT
from backend.app.rag.parser import CorpusParser
from backend.app.schemas.scheme import ProcessedCorpus, SchemeData


def test_corpus_parser_build():
    """Verify that CorpusParser reads all raw files and builds ProcessedCorpus correctly."""
    parser = CorpusParser()
    corpus = parser.build_processed_corpus()

    assert corpus.total_schemes == 5
    assert len(corpus.schemes) == 5
    assert corpus.amc == "HDFC Asset Management Company Limited"
    assert corpus.general_operations is not None


def test_processed_schemes_content():
    """Verify all 5 schemes have valid parameters and whitelisted Groww URLs."""
    processed_path = PROJECT_ROOT / "data" / "processed" / "schemes.json"
    assert processed_path.exists(), "data/processed/schemes.json must exist"

    with open(processed_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    corpus = ProcessedCorpus(**data)
    assert corpus.total_schemes == 5

    scheme_codes = {s.scheme_code for s in corpus.schemes}
    expected_codes = {
        "hdfc-mid-cap-fund-direct-growth",
        "hdfc-small-cap-fund-direct-growth",
        "hdfc-gold-etf-fund-of-fund-direct-plan-growth",
        "hdfc-large-cap-fund-direct-growth",
        "hdfc-elss-tax-saver-fund-direct-plan-growth",
    }
    assert scheme_codes == expected_codes

    for scheme in corpus.schemes:
        assert scheme.official_source_url.startswith("https://groww.in/mutual-funds")
        assert scheme.expense_ratio.direct_plan_percentage > 0
        assert scheme.investment_limits.min_sip_amount > 0
        assert scheme.benchmark_index != ""
        assert scheme.riskometer in {"Very High", "High", "Moderate"}

        if scheme.scheme_code == "hdfc-elss-tax-saver-fund-direct-plan-growth":
            assert scheme.lock_in_period.has_lock_in is True
            assert scheme.lock_in_period.duration_years == 3
            assert scheme.investment_limits.min_sip_amount == 500
        else:
            assert scheme.lock_in_period.has_lock_in is False
            assert scheme.lock_in_period.duration_years == 0


def test_url_validation_rejection():
    """Verify SchemeData rejects non-Groww URLs."""
    with open(PROJECT_ROOT / "data" / "raw" / "hdfc_mid_cap_fund.json", "r") as f:
        raw = json.load(f)

    raw["official_source_url"] = "https://unauthorized-domain.com/scheme"
    with pytest.raises(ValueError, match="Invalid official_source_url"):
        SchemeData(**raw)
