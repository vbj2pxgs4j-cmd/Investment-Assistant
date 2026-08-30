"""Parser and normalizer module for Mutual Fund FAQ Assistant corpus.

Reads raw JSON files from data/raw/, validates schema constraints, normalizes text
and numerical parameters, and outputs the unified data/processed/schemes.json dataset.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

from backend.app.core.config import PROJECT_ROOT, get_settings
from backend.app.core.logging import get_logger
from backend.app.schemas.scheme import (
    GeneralOperationsData,
    ProcessedCorpus,
    SchemeData,
)

logger = get_logger("rag.parser")


class CorpusParser:
    """Parser and normalizer for mutual fund scheme source files."""

    def __init__(self, raw_dir: Optional[Path] = None, processed_dir: Optional[Path] = None):
        self.raw_dir = raw_dir or (PROJECT_ROOT / "data" / "raw")
        self.processed_dir = processed_dir or (PROJECT_ROOT / "data" / "processed")
        self.manifest_path = self.raw_dir / "sources_manifest.json"

    def load_manifest(self) -> Dict:
        """Load sources manifest registry."""
        if not self.manifest_path.exists():
            raise FileNotFoundError(f"Sources manifest not found at {self.manifest_path}")
        with open(self.manifest_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def parse_scheme_file(self, file_path: Path) -> SchemeData:
        """Parse, normalize, and validate a single scheme JSON file."""
        if not file_path.exists():
            raise FileNotFoundError(f"Scheme file not found at {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        # Normalize text fields (strip extra whitespace)
        if "scheme_name" in raw_data:
            raw_data["scheme_name"] = raw_data["scheme_name"].strip()
        if "benchmark_index" in raw_data:
            raw_data["benchmark_index"] = raw_data["benchmark_index"].strip()

        # Validate with Pydantic SchemeData model
        scheme = SchemeData(**raw_data)
        return scheme

    def parse_operations_file(self, file_path: Path) -> GeneralOperationsData:
        """Parse, normalize, and validate general operations JSON file."""
        if not file_path.exists():
            raise FileNotFoundError(f"Operations file not found at {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            raw_data = json.load(f)

        return GeneralOperationsData(**raw_data)

    def build_processed_corpus(self, last_updated: Optional[str] = None) -> ProcessedCorpus:
        """Parse all scheme files registered in manifest and build unified ProcessedCorpus."""
        manifest = self.load_manifest()
        schemes_list: List[SchemeData] = []
        operations_data: Optional[GeneralOperationsData] = None

        for source in manifest.get("sources", []):
            relative_file = source.get("raw_file")
            file_path = PROJECT_ROOT / relative_file

            if source.get("id") == "general-operations":
                operations_data = self.parse_operations_file(file_path)
            else:
                scheme = self.parse_scheme_file(file_path)
                schemes_list.append(scheme)
                logger.info("Successfully parsed and validated scheme: %s (%s)", scheme.scheme_name, scheme.scheme_code)

        if not operations_data:
            general_ops_path = self.raw_dir / "general_operations.json"
            operations_data = self.parse_operations_file(general_ops_path)

        corpus_date = last_updated or (schemes_list[0].last_updated if schemes_list else "2024-04-01")

        corpus = ProcessedCorpus(
            amc=manifest.get("amc", "HDFC Asset Management Company Limited"),
            total_schemes=len(schemes_list),
            last_updated=corpus_date,
            schemes=schemes_list,
            general_operations=operations_data,
        )

        return corpus

    def save_processed_corpus(self, corpus: Optional[ProcessedCorpus] = None, output_filename: str = "schemes.json", last_updated: Optional[str] = None) -> Path:
        """Save the processed corpus to data/processed/schemes.json."""
        if corpus is None:
            corpus = self.build_processed_corpus(last_updated=last_updated)

        self.processed_dir.mkdir(parents=True, exist_ok=True)
        output_path = self.processed_dir / output_filename

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(corpus.model_dump(), f, indent=2, ensure_ascii=False)

        logger.info("Saved normalized corpus to %s (Total schemes: %d)", output_path, corpus.total_schemes)
        return output_path


def parse_and_normalize_corpus() -> Path:
    """Convenience helper to parse raw files and generate data/processed/schemes.json."""
    parser = CorpusParser()
    return parser.save_processed_corpus()


if __name__ == "__main__":
    out_file = parse_and_normalize_corpus()
    print(f"Successfully processed and normalized corpus at: {out_file}")
