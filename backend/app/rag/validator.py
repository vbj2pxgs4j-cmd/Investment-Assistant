"""Data integrity and compliance validator for processed corpus chunks."""

import json
from pathlib import Path
from typing import Dict, List, Optional, Set

from backend.app.core.config import PROJECT_ROOT
from backend.app.core.logging import get_logger
from backend.app.schemas.chunk import ChunkCollection, KnowledgeChunk

logger = get_logger("rag.validator")

EXPECTED_SCHEME_CODES = {
    "hdfc-mid-cap-fund-direct-growth",
    "hdfc-small-cap-fund-direct-growth",
    "hdfc-gold-etf-fund-of-fund-direct-plan-growth",
    "hdfc-large-cap-fund-direct-growth",
    "hdfc-elss-tax-saver-fund-direct-plan-growth",
}

EXPECTED_PARAMETERS = {
    "fund_overview",
    "expense_ratio",
    "exit_load",
    "investment_limits",
    "lock_in_period",
    "taxation",
    "operations",
}

EXPECTED_GENERAL_PARAMETERS = {
    "statement_download_general",
    "capital_gains_report_general",
    "educational_resources_general",
}


class CorpusValidator:
    """Validates structural integrity, metadata completeness, and URL compliance of chunks."""

    def __init__(self, chunks_file: Optional[Path] = None):
        self.chunks_file = chunks_file or (PROJECT_ROOT / "data" / "processed" / "chunks.json")

    def load_chunks(self) -> ChunkCollection:
        """Load and parse the chunks JSON file."""
        if not self.chunks_file.exists():
            raise FileNotFoundError(f"Chunks file not found at {self.chunks_file}")

        with open(self.chunks_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        return ChunkCollection(**data)

    def validate(self) -> Dict[str, bool]:
        """Execute full validation suite against all chunks."""
        collection = self.load_chunks()
        chunks = collection.chunks

        errors: List[str] = []

        # 1. Total chunk count check (Expect exactly 38 chunks)
        if len(chunks) != 38:
            errors.append(f"Expected exactly 38 chunks, found {len(chunks)}")

        # 2. Scheme code coverage
        found_schemes: Set[str] = {c.scheme_code for c in chunks if c.scheme_code != "general-operations"}
        missing_schemes = EXPECTED_SCHEME_CODES - found_schemes
        if missing_schemes:
            errors.append(f"Missing scheme codes in chunks: {missing_schemes}")

        # 3. Parameter coverage per scheme
        for scheme_code in EXPECTED_SCHEME_CODES:
            scheme_params = {c.parameter for c in chunks if c.scheme_code == scheme_code}
            missing_params = EXPECTED_PARAMETERS - scheme_params
            if missing_params:
                errors.append(f"Scheme {scheme_code} is missing parameters: {missing_params}")

        # 4. General parameters coverage
        general_params = {c.parameter for c in chunks if c.scheme_code == "general-operations"}
        missing_general = EXPECTED_GENERAL_PARAMETERS - general_params
        if missing_general:
            errors.append(f"Missing general operations parameters: {missing_general}")

        # 5. Individual Chunk integrity checks
        seen_chunk_ids: Set[str] = set()
        for idx, chunk in enumerate(chunks):
            # Unique ID
            if chunk.chunk_id in seen_chunk_ids:
                errors.append(f"Duplicate chunk_id detected: {chunk.chunk_id}")
            seen_chunk_ids.add(chunk.chunk_id)

            # Non-empty content
            if not chunk.content or len(chunk.content.strip()) < 10:
                errors.append(f"Chunk {chunk.chunk_id} has insufficient content")

            # URL whitelisting
            if not (chunk.official_source_url.startswith("https://groww.in/") or chunk.official_source_url.startswith("http://groww.in/")):
                errors.append(f"Chunk {chunk.chunk_id} has non-whitelisted URL: {chunk.official_source_url}")

            # Non-empty keywords
            if not chunk.keywords:
                errors.append(f"Chunk {chunk.chunk_id} has empty keywords list")

        if errors:
            error_msg = "\n- ".join(errors)
            logger.error("Corpus validation failed with %d errors:\n- %s", len(errors), error_msg)
            raise ValueError(f"Corpus validation failed:\n- {error_msg}")

        logger.info("Corpus validation passed successfully for %d chunks.", len(chunks))
        return {"status": True, "total_chunks": len(chunks), "total_schemes": len(found_schemes)}


def validate_corpus() -> Dict[str, bool]:
    """Helper function to run corpus validation."""
    validator = CorpusValidator()
    return validator.validate()


if __name__ == "__main__":
    result = validate_corpus()
    print("Validation passed:", result)
