"""Unit and integration tests for Phase 7 Daily Ingestion Scheduler Pipeline."""

import pytest
from pathlib import Path
from unittest.mock import AsyncMock, patch

from backend.app.rag.daily_ingestion import DailyIngestionPipeline
from backend.app.rag.scraper import SchemeScraper, TARGET_SCHEMES_REGISTRY
from backend.app.rag.retriever import SchemeFilteredRetriever
from backend.app.rag.validator import CorpusValidator


@pytest.mark.asyncio
async def test_scraper_target_registry_coverage():
    """Verify scraper registry contains all 5 required HDFC schemes."""
    assert len(TARGET_SCHEMES_REGISTRY) == 5
    scheme_ids = [s["id"] for s in TARGET_SCHEMES_REGISTRY]
    assert "hdfc-mid-cap-fund-direct-growth" in scheme_ids
    assert "hdfc-small-cap-fund-direct-growth" in scheme_ids
    assert "hdfc-gold-etf-fund-of-fund-direct-plan-growth" in scheme_ids
    assert "hdfc-large-cap-fund-direct-growth" in scheme_ids
    assert "hdfc-elss-tax-saver-fund-direct-plan-growth" in scheme_ids


@pytest.mark.asyncio
async def test_scraper_fetch_scheme_data():
    """Verify SchemeScraper returns properly formatted scheme data with timestamp."""
    scraper = SchemeScraper()
    test_cfg = TARGET_SCHEMES_REGISTRY[0]
    data = await scraper.fetch_scheme_data(test_cfg, date_str="2026-08-30")
    
    assert data["scheme_code"] == "hdfc-mid-cap-fund-direct-growth"
    assert data["last_updated"] == "2026-08-30"
    assert data["official_source_url"] == "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth"


@pytest.mark.asyncio
async def test_daily_ingestion_end_to_end_pipeline():
    """Verify DailyIngestionPipeline runs all 5 stages successfully."""
    pipeline = DailyIngestionPipeline()
    results = await pipeline.run_pipeline(
        custom_date="2026-08-30",
        force_reload=False,
        skip_scraping=True,
    )

    assert results["status"] == "success"
    assert results["target_date"] == "2026-08-30"
    assert "normalization" in results["stages"]
    assert "chunking" in results["stages"]
    assert "validation" in results["stages"]
    assert "vector_indexing" in results["stages"]

    assert results["stages"]["chunking"]["total_chunks"] == 38
    assert results["stages"]["validation"]["total_validated"] == 38
    assert results["stages"]["vector_indexing"]["indexed_count"] >= 38


@pytest.mark.asyncio
async def test_retrieval_verification_after_pipeline():
    """Verify that SchemeFilteredRetriever retrieves accurate chunks from the updated index."""
    pipeline = DailyIngestionPipeline()
    await pipeline.run_pipeline(skip_scraping=True, force_reload=False)

    retriever = SchemeFilteredRetriever(vector_store=pipeline.vector_store)
    result = retriever.retrieve("What is the exit load for HDFC Small Cap Fund?")

    assert result.primary_chunk is not None
    assert result.primary_chunk.scheme_code == "hdfc-small-cap-fund-direct-growth"
    assert result.primary_chunk.parameter == "exit_load"
    assert "groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth" in result.official_source_url


@pytest.mark.asyncio
async def test_validation_barrier_blocks_corrupt_data():
    """Verify that validation barrier halts pipeline execution when chunk validation fails."""
    pipeline = DailyIngestionPipeline()
    
    # Mock validator to simulate a failure
    failing_validator = CorpusValidator()
    failing_validator.validate = lambda: {"is_valid": False, "errors": ["Mock schema corruption detected"]}
    pipeline.validator = failing_validator

    with pytest.raises(ValueError, match="Ingestion aborted"):
        await pipeline.run_pipeline(skip_scraping=True)
