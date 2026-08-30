"""Unit tests for the SchemeChunker engine and CorpusValidator."""

import json
from pathlib import Path
import pytest

from backend.app.core.config import PROJECT_ROOT
from backend.app.rag.chunker import SchemeChunker
from backend.app.rag.validator import CorpusValidator, validate_corpus
from backend.app.schemas.chunk import ChunkCollection, KnowledgeChunk


def test_scheme_chunker_generates_all_chunks():
    """Verify that SchemeChunker generates exactly 38 atomic chunks."""
    chunker = SchemeChunker()
    collection = chunker.chunk_all()

    assert collection.total_chunks == 38
    assert len(collection.chunks) == 38

    # 5 schemes * 7 parameters = 35 scheme chunks
    scheme_chunks = [c for c in collection.chunks if c.scheme_code != "general-operations"]
    assert len(scheme_chunks) == 35

    # 3 general operations chunks
    general_chunks = [c for c in collection.chunks if c.scheme_code == "general-operations"]
    assert len(general_chunks) == 3


def test_chunk_parameters_and_values():
    """Verify specific parameter values and assertions for representative schemes."""
    chunker = SchemeChunker()
    collection = chunker.chunk_all()
    chunk_map = {c.chunk_id: c for c in collection.chunks}

    # Test ELSS lock-in chunk
    elss_lockin = chunk_map.get("hdfc_elss_tax_saver_fund_direct_plan_growth_lock_in_period")
    assert elss_lockin is not None
    assert "3-year" in elss_lockin.content or "3 years" in elss_lockin.content
    assert elss_lockin.metadata.get("has_lock_in") is True
    assert elss_lockin.metadata.get("duration_years") == 3
    assert elss_lockin.official_source_url == "https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth"

    # Test Mid Cap expense ratio chunk
    midcap_ter = chunk_map.get("hdfc_mid_cap_fund_direct_growth_expense_ratio")
    assert midcap_ter is not None
    assert "0.74%" in midcap_ter.content
    assert midcap_ter.metadata.get("direct_plan_percentage") == 0.74

    # Test Small Cap exit load chunk
    smallcap_exit = chunk_map.get("hdfc_small_cap_fund_direct_growth_exit_load")
    assert smallcap_exit is not None
    assert "1.00%" in smallcap_exit.content
    assert smallcap_exit.metadata.get("holding_period_threshold_days") == 365

    # Test Gold ETF exit load chunk
    gold_exit = chunk_map.get("hdfc_gold_etf_fund_of_fund_direct_plan_growth_exit_load")
    assert gold_exit is not None
    assert "15 days" in gold_exit.content
    assert gold_exit.metadata.get("holding_period_threshold_days") == 15


def test_validator_passes():
    """Verify that CorpusValidator confirms data integrity of chunks.json."""
    validator = CorpusValidator()
    result = validator.validate()

    assert result["status"] is True
    assert result["total_chunks"] == 38
    assert result["total_schemes"] == 5
