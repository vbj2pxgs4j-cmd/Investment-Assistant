"""Parameter-Domain Chunking Engine for Mutual Fund FAQ Assistant.

Decomposes structured scheme records from data/processed/schemes.json into
38 atomic, semantically coherent factual chunks with complete metadata tags.
"""

import json
from pathlib import Path
from typing import List, Optional

from backend.app.core.config import PROJECT_ROOT
from backend.app.core.logging import get_logger
from backend.app.schemas.chunk import ChunkCollection, KnowledgeChunk
from backend.app.schemas.scheme import ProcessedCorpus, SchemeData

logger = get_logger("rag.chunker")


class SchemeChunker:
    """Domain-aware chunker that decomposes mutual fund facts into atomic parameter chunks."""

    def __init__(self, processed_file: Optional[Path] = None, output_file: Optional[Path] = None):
        self.processed_file = processed_file or (PROJECT_ROOT / "data" / "processed" / "schemes.json")
        self.output_file = output_file or (PROJECT_ROOT / "data" / "processed" / "chunks.json")

    def load_processed_corpus(self) -> ProcessedCorpus:
        """Load normalized processed corpus from JSON."""
        if not self.processed_file.exists():
            raise FileNotFoundError(f"Processed schemes file not found at {self.processed_file}")
        with open(self.processed_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return ProcessedCorpus(**data)

    def _generate_scheme_chunks(self, scheme: SchemeData) -> List[KnowledgeChunk]:
        """Generate 7 parameter-domain knowledge chunks for a single mutual fund scheme."""
        code = scheme.scheme_code
        name = scheme.scheme_name
        cat = scheme.category
        url = scheme.official_source_url
        updated = scheme.last_updated
        base_id = code.replace("-", "_")

        chunks: List[KnowledgeChunk] = []

        # 1. Fund Overview
        overview_content = (
            f"{name} ({scheme.plan_type}) is managed by {scheme.amc} under the {cat} category. "
            f"It is an {scheme.fund_type}. "
            f"The fund tracks the {scheme.benchmark_index} benchmark and is classified as '{scheme.riskometer}' risk on the SEBI Riskometer."
        )
        chunks.append(
            KnowledgeChunk(
                chunk_id=f"{base_id}_fund_overview",
                scheme_code=code,
                scheme_name=name,
                category=cat,
                parameter="fund_overview",
                title=f"{name} - Fund Overview & Classification",
                content=overview_content,
                official_source_url=url,
                last_updated=updated,
                keywords=[name.lower(), "fund overview", "category", "benchmark", "riskometer", scheme.benchmark_index.lower(), scheme.riskometer.lower()],
                metadata={
                    "benchmark": scheme.benchmark_index,
                    "riskometer": scheme.riskometer,
                    "amc": scheme.amc,
                    "fund_type": scheme.fund_type,
                },
            )
        )

        # 2. Expense Ratio (TER)
        chunks.append(
            KnowledgeChunk(
                chunk_id=f"{base_id}_expense_ratio",
                scheme_code=code,
                scheme_name=name,
                category=cat,
                parameter="expense_ratio",
                title=f"{name} - Expense Ratio (TER)",
                content=scheme.expense_ratio.description,
                official_source_url=url,
                last_updated=updated,
                keywords=[name.lower(), "expense ratio", "ter", "direct plan ter", "management fee", "charges"],
                metadata={
                    "direct_plan_percentage": scheme.expense_ratio.direct_plan_percentage,
                    "regular_plan_percentage": scheme.expense_ratio.regular_plan_percentage,
                },
            )
        )

        # 3. Exit Load
        chunks.append(
            KnowledgeChunk(
                chunk_id=f"{base_id}_exit_load",
                scheme_code=code,
                scheme_name=name,
                category=cat,
                parameter="exit_load",
                title=f"{name} - Exit Load & Holding Duration",
                content=scheme.exit_load.description,
                official_source_url=url,
                last_updated=updated,
                keywords=[name.lower(), "exit load", "redemption fee", "holding period", "early withdrawal charge", "lock-in"],
                metadata={
                    "percentage": scheme.exit_load.percentage,
                    "holding_period_threshold_days": scheme.exit_load.holding_period_threshold_days,
                },
            )
        )

        # 4. Investment Limits (SIP & Lump Sum)
        chunks.append(
            KnowledgeChunk(
                chunk_id=f"{base_id}_investment_limits",
                scheme_code=code,
                scheme_name=name,
                category=cat,
                parameter="investment_limits",
                title=f"{name} - Minimum SIP & Lump Sum Limits",
                content=scheme.investment_limits.description,
                official_source_url=url,
                last_updated=updated,
                keywords=[name.lower(), "minimum sip", "min sip", "lump sum", "minimum investment", "initial purchase", "additional purchase"],
                metadata={
                    "min_sip_amount": scheme.investment_limits.min_sip_amount,
                    "min_lump_sum_amount": scheme.investment_limits.min_lump_sum_amount,
                    "min_additional_investment": scheme.investment_limits.min_additional_investment,
                    "sip_frequency": scheme.investment_limits.sip_frequency,
                },
            )
        )

        # 5. Lock-in Period
        chunks.append(
            KnowledgeChunk(
                chunk_id=f"{base_id}_lock_in_period",
                scheme_code=code,
                scheme_name=name,
                category=cat,
                parameter="lock_in_period",
                title=f"{name} - Statutory Lock-in Period",
                content=scheme.lock_in_period.description,
                official_source_url=url,
                last_updated=updated,
                keywords=[name.lower(), "lock-in period", "lock in", "holding period", "elss lock in", "3 years lock-in", "maturity"],
                metadata={
                    "has_lock_in": scheme.lock_in_period.has_lock_in,
                    "duration_years": scheme.lock_in_period.duration_years,
                },
            )
        )

        # 6. Taxation
        tax_parts = []
        if scheme.taxation.tax_deduction:
            tax_parts.append(scheme.taxation.tax_deduction)
        if scheme.taxation.short_term_capital_gains:
            tax_parts.append(scheme.taxation.short_term_capital_gains)
        if scheme.taxation.long_term_capital_gains:
            tax_parts.append(scheme.taxation.long_term_capital_gains)
        if scheme.taxation.tax_regime:
            tax_parts.append(scheme.taxation.tax_regime)
        tax_content = " ".join(tax_parts)

        chunks.append(
            KnowledgeChunk(
                chunk_id=f"{base_id}_taxation",
                scheme_code=code,
                scheme_name=name,
                category=cat,
                parameter="taxation",
                title=f"{name} - Mutual Fund Taxation & Capital Gains",
                content=tax_content,
                official_source_url=url,
                last_updated=updated,
                keywords=[name.lower(), "taxation", "stcg", "ltcg", "capital gains", "80c", "tax benefit", "tax deduction"],
                metadata={
                    "equity_taxation": scheme.taxation.equity_taxation,
                },
            )
        )

        # 7. Operations & Statements
        ops_content = f"{scheme.operations.account_statement_procedure} {scheme.operations.folio_lookup}"
        chunks.append(
            KnowledgeChunk(
                chunk_id=f"{base_id}_operations",
                scheme_code=code,
                scheme_name=name,
                category=cat,
                parameter="operations",
                title=f"{name} - Account Statements & Folio Verification",
                content=ops_content,
                official_source_url=url,
                last_updated=updated,
                keywords=[name.lower(), "download statement", "account statement", "capital gains report", "folio number", "cams", "kfintech"],
                metadata={},
            )
        )

        return chunks

    def _generate_general_operations_chunks(self, corpus: ProcessedCorpus) -> List[KnowledgeChunk]:
        """Generate 3 operational and educational knowledge chunks."""
        ops = corpus.general_operations
        url = ops.official_source_url
        updated = ops.last_updated
        cat = ops.category

        chunks: List[KnowledgeChunk] = []

        # 8. Statement Download General
        st_content = (
            f"{ops.statement_download.get('groww_procedure', '')} "
            f"{ops.statement_download.get('amc_procedure', '')} "
            f"{ops.statement_download.get('cas_procedure', '')}"
        )
        chunks.append(
            KnowledgeChunk(
                chunk_id="general_operations_statement_download",
                scheme_code="general-operations",
                scheme_name="General Mutual Fund Operations",
                category=cat,
                parameter="statement_download_general",
                title="Mutual Fund Account Statement Download Procedure",
                content=st_content,
                official_source_url=url,
                last_updated=updated,
                keywords=["download statement", "account statement", "groww statement", "amc statement", "cas statement", "cams", "kfintech"],
                metadata={"procedure_type": "account_statement"},
            )
        )

        # 9. Capital Gains Report General
        cg_content = (
            f"{ops.capital_gains_report.get('purpose', '')} "
            f"{ops.capital_gains_report.get('download_steps', '')}"
        )
        chunks.append(
            KnowledgeChunk(
                chunk_id="general_operations_capital_gains_report",
                scheme_code="general-operations",
                scheme_name="General Mutual Fund Operations",
                category=cat,
                parameter="capital_gains_report_general",
                title="Mutual Fund Capital Gains Tax Report Download (ITR Filing)",
                content=cg_content,
                official_source_url=url,
                last_updated=updated,
                keywords=["capital gains report", "tax statement", "schedule 112a", "itr filing", "tax report download", "groww tax report"],
                metadata={"procedure_type": "capital_gains"},
            )
        )

        # 10. Educational Resources General
        edu_content = (
            f"For official investor education and mutual fund guidelines, consult Groww Mutual Funds ({ops.educational_resources.get('groww_mf_hub', '')}), "
            f"AMFI Investor Education ({ops.educational_resources.get('amfi_investor_education', '')}), or the SEBI Investor Portal ({ops.educational_resources.get('sebi_investor_portal', '')}). "
            f"These official portals offer investor guidance, regulatory circulars, and dispute resolution workflows."
        )
        chunks.append(
            KnowledgeChunk(
                chunk_id="general_operations_educational_resources",
                scheme_code="general-operations",
                scheme_name="General Mutual Fund Operations",
                category=cat,
                parameter="educational_resources_general",
                title="Mutual Fund Educational & Regulatory Resources",
                content=edu_content,
                official_source_url=url,
                last_updated=updated,
                keywords=["amfi", "sebi", "investor education", "guidelines", "groww mutual funds", "complaint", "regulations"],
                metadata={"resource_type": "education"},
            )
        )

        return chunks

    def chunk_all(self) -> ChunkCollection:
        """Process all schemes and operations in the corpus into an atomic ChunkCollection."""
        corpus = self.load_processed_corpus()
        all_chunks: List[KnowledgeChunk] = []

        for scheme in corpus.schemes:
            scheme_chunks = self._generate_scheme_chunks(scheme)
            all_chunks.extend(scheme_chunks)
            logger.info("Generated %d chunks for scheme: %s", len(scheme_chunks), scheme.scheme_name)

        general_chunks = self._generate_general_operations_chunks(corpus)
        all_chunks.extend(general_chunks)
        logger.info("Generated %d general operations chunks", len(general_chunks))

        collection = ChunkCollection(
            total_chunks=len(all_chunks),
            last_updated=corpus.last_updated,
            chunks=all_chunks,
        )

        return collection

    def save_chunks(self, collection: Optional[ChunkCollection] = None) -> Path:
        """Save generated chunk collection to data/processed/chunks.json."""
        if collection is None:
            collection = self.chunk_all()

        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.output_file, "w", encoding="utf-8") as f:
            json.dump(collection.model_dump(), f, indent=2, ensure_ascii=False)

        logger.info("Successfully persisted %d knowledge chunks to %s", collection.total_chunks, self.output_file)
        return self.output_file


def chunk_corpus() -> Path:
    """Convenience helper to chunk the processed corpus and save chunks.json."""
    chunker = SchemeChunker()
    return chunker.save_chunks()


if __name__ == "__main__":
    out_path = chunk_corpus()
    print(f"Successfully generated chunks at: {out_path}")
