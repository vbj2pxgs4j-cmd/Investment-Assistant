"""Daily Ingestion Orchestrator for Mutual Fund FAQ Assistant RAG Pipeline.

Orchestrates the 5-stage automated ingestion lifecycle:
1. Live Groww Scheme Scraping & Raw Snapshot Sync
2. Normalization & Schema Validation (data/processed/schemes.json)
3. Atomic Parameter Chunking (data/processed/chunks.json)
4. Data Integrity & Validation Barrier (CorpusValidator)
5. Dense Embeddings Calculation & ChromaDB Index Upsert (VectorStoreService)
"""

import argparse
import asyncio
import json
import logging
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from backend.app.core.config import PROJECT_ROOT
from backend.app.core.logging import setup_logging
from backend.app.rag.chunker import SchemeChunker
from backend.app.rag.parser import CorpusParser
from backend.app.rag.scraper import SchemeScraper
from backend.app.rag.validator import CorpusValidator
from backend.app.rag.vector_store import VectorStoreService

logger = logging.getLogger("rag.daily_ingestion")


class DailyIngestionPipeline:
    """End-to-end scheduler orchestrator for daily mutual fund data refresh."""

    def __init__(
        self,
        scraper: Optional[SchemeScraper] = None,
        parser: Optional[CorpusParser] = None,
        chunker: Optional[SchemeChunker] = None,
        validator: Optional[CorpusValidator] = None,
        vector_store: Optional[VectorStoreService] = None,
    ) -> None:
        self.scraper = scraper or SchemeScraper()
        self.parser = parser or CorpusParser()
        self.chunker = chunker or SchemeChunker()
        self.validator = validator or CorpusValidator()
        self.vector_store = vector_store or VectorStoreService()

    async def run_pipeline(
        self,
        custom_date: Optional[str] = None,
        force_reload: bool = True,
        skip_scraping: bool = False,
    ) -> Dict[str, Any]:
        """Execute all 5 stages of the daily ingestion and re-indexing pipeline.

        Args:
            custom_date: Optional ISO date string (YYYY-MM-DD) for updates.
            force_reload: Whether to force-reload ChromaDB index.
            skip_scraping: If True, uses existing raw files without live network requests.

        Returns:
            Dictionary containing execution metrics and stage-by-stage results.
        """
        start_time = time.perf_counter()
        target_date = custom_date or datetime.now(timezone.utc).strftime("%Y-%m-%d")
        metrics: Dict[str, Any] = {
            "target_date": target_date,
            "status": "in_progress",
            "stages": {},
        }

        logger.info("=================================================================")
        logger.info("Starting Daily Ingestion Pipeline for date: %s", target_date)
        logger.info("=================================================================")

        # -------------------------------------------------------------------------
        # Stage 1: Scraping & Raw Snapshot Synchronization
        # -------------------------------------------------------------------------
        s1_start = time.perf_counter()
        if not skip_scraping:
            logger.info("[Stage 1/5] Fetching live fund data and synchronizing raw snapshots...")
            updated_raw_files = await self.scraper.sync_all_schemes(custom_date=target_date)
            s1_duration = round((time.perf_counter() - s1_start) * 1000, 2)
            metrics["stages"]["scraping"] = {
                "status": "success",
                "files_updated": len(updated_raw_files),
                "duration_ms": s1_duration,
            }
            logger.info("Stage 1 completed in %.2f ms (%d files updated).", s1_duration, len(updated_raw_files))
        else:
            metrics["stages"]["scraping"] = {"status": "skipped", "duration_ms": 0}
            logger.info("[Stage 1/5] Scraping skipped as requested.")

        # -------------------------------------------------------------------------
        # Stage 2: Normalization & Processed Corpus Generation
        # -------------------------------------------------------------------------
        s2_start = time.perf_counter()
        logger.info("[Stage 2/5] Normalizing raw schemes into data/processed/schemes.json...")
        processed_path = self.parser.save_processed_corpus(last_updated=target_date)
        s2_duration = round((time.perf_counter() - s2_start) * 1000, 2)
        metrics["stages"]["normalization"] = {
            "status": "success",
            "output_file": str(processed_path.relative_to(PROJECT_ROOT)),
            "duration_ms": s2_duration,
        }
        logger.info("Stage 2 completed in %.2f ms (Saved %s).", s2_duration, processed_path.name)

        # -------------------------------------------------------------------------
        # Stage 3: Atomic Parameter Chunking
        # -------------------------------------------------------------------------
        s3_start = time.perf_counter()
        logger.info("[Stage 3/5] Generating atomic knowledge chunks in data/processed/chunks.json...")
        chunks_collection = self.chunker.save_chunks()
        s3_duration = round((time.perf_counter() - s3_start) * 1000, 2)
        metrics["stages"]["chunking"] = {
            "status": "success",
            "total_chunks": chunks_collection.total_chunks,
            "duration_ms": s3_duration,
        }
        logger.info("Stage 3 completed in %.2f ms (%d chunks created).", s3_duration, chunks_collection.total_chunks)

        # -------------------------------------------------------------------------
        # Stage 4: Validation Barrier (Integrity Check)
        # -------------------------------------------------------------------------
        s4_start = time.perf_counter()
        logger.info("[Stage 4/5] Executing data validation barrier against chunks...")
        try:
            validation_report = self.validator.validate()
            s4_duration = round((time.perf_counter() - s4_start) * 1000, 2)
            metrics["stages"]["validation"] = {
                "status": "success",
                "total_validated": validation_report.get("total_chunks", 38),
                "duration_ms": s4_duration,
            }
            logger.info("Stage 4 completed in %.2f ms (Validation Passed: 100%% compliant).", s4_duration)
        except Exception as val_err:
            s4_duration = round((time.perf_counter() - s4_start) * 1000, 2)
            logger.error("Validation barrier FAILED: %s. Halting ChromaDB update.", val_err)
            metrics["status"] = "failed"
            metrics["error"] = str(val_err)
            metrics["stages"]["validation"] = {
                "status": "failed",
                "error": str(val_err),
                "duration_ms": s4_duration,
            }
            raise ValueError(f"Ingestion aborted: Validation barrier failed: {val_err}") from val_err

        # -------------------------------------------------------------------------
        # Stage 5: Dense Embeddings & ChromaDB Index Upsert
        # -------------------------------------------------------------------------
        s5_start = time.perf_counter()
        logger.info("[Stage 5/5] Re-indexing vector store collection 'mutual_fund_facts' in ChromaDB...")
        indexed_count = self.vector_store.initialize_store(force_reload=force_reload)
        s5_duration = round((time.perf_counter() - s5_start) * 1000, 2)
        metrics["stages"]["vector_indexing"] = {
            "status": "success",
            "indexed_count": indexed_count,
            "duration_ms": s5_duration,
        }
        logger.info("Stage 5 completed in %.2f ms (%d vectors indexed in ChromaDB).", s5_duration, indexed_count)

        total_duration = round((time.perf_counter() - start_time) * 1000, 2)
        metrics["status"] = "success"
        metrics["total_duration_ms"] = total_duration

        logger.info("=================================================================")
        logger.info("Daily Ingestion Pipeline SUCCEEDED in %.2f ms for date %s", total_duration, target_date)
        logger.info("=================================================================")

        return metrics


async def main() -> None:
    """CLI entrypoint for daily scheduled ingestion."""
    setup_logging("INFO")
    parser = argparse.ArgumentParser(description="Mutual Fund FAQ Assistant Daily Ingestion Scheduler CLI")
    parser.add_argument("--date", type=str, default=None, help="Target ISO date for ingestion update (YYYY-MM-DD)")
    parser.add_argument("--skip-scraping", action="store_true", help="Skip live network scraping and use local raw files")
    parser.add_argument("--verify", action="store_true", help="Run retrieval accuracy verification test after pipeline")
    parser.add_argument("--force", action="store_true", default=True, help="Force reload ChromaDB vector collection")

    args = parser.parse_args()

    pipeline = DailyIngestionPipeline()
    try:
        results = await pipeline.run_pipeline(
            custom_date=args.date,
            force_reload=args.force,
            skip_scraping=args.skip_scraping,
        )
        print(json.dumps(results, indent=2))

        if args.verify:
            logger.info("Running retrieval verification test against newly indexed vector store...")
            from backend.app.rag.retriever import SchemeFilteredRetriever
            retriever = SchemeFilteredRetriever(vector_store=pipeline.vector_store)
            test_res = retriever.retrieve("What is the exit load for HDFC Small Cap Fund?")
            assert test_res.primary_chunk is not None, "Verification failed: Could not retrieve primary chunk"
            logger.info("Verification PASSED: Retrieved chunk '%s' successfully.", test_res.primary_chunk.chunk_id)

    except Exception as exc:
        logger.exception("Daily ingestion pipeline failed: %s", exc)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
