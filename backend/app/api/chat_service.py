"""Chat Pipeline Service orchestrating PII, Intent Routing, Retrieval, and Grounded Generation."""

import json
import logging
import time
from typing import Any, Dict, List, Optional

from backend.app.core.config import PROJECT_ROOT, get_settings
from backend.app.guardrails.intent_router import IntentRouter
from backend.app.guardrails.pii_filter import PIIFilter
from backend.app.guardrails.refusal_handler import RefusalHandler
from backend.app.rag.generator import GroundedGenerator
from backend.app.rag.retriever import SchemeFilteredRetriever
from backend.app.rag.vector_store import VectorStoreService
from backend.app.schemas.chat import ChatQueryResponse, SchemeSummary
from backend.app.schemas.generation import GenerationInput
from backend.app.schemas.guardrails import QueryIntent
from backend.app.schemas.retrieval import ResolutionStatus

logger = logging.getLogger(__name__)


class ChatPipelineService:
    """Singleton service executing the complete 4-tier Facts-Only RAG pipeline."""

    def __init__(
        self,
        pii_filter: Optional[PIIFilter] = None,
        intent_router: Optional[IntentRouter] = None,
        refusal_handler: Optional[RefusalHandler] = None,
        vector_store: Optional[VectorStoreService] = None,
        retriever: Optional[SchemeFilteredRetriever] = None,
        generator: Optional[GroundedGenerator] = None,
    ) -> None:
        self.settings = get_settings()
        self.pii_filter = pii_filter or PIIFilter()
        self.intent_router = intent_router or IntentRouter()
        self.refusal_handler = refusal_handler or RefusalHandler()
        self.vector_store = vector_store or VectorStoreService()
        self.retriever = retriever or SchemeFilteredRetriever(vector_store=self.vector_store)
        self.generator = generator or GroundedGenerator()

    def initialize(self) -> None:
        """Pre-warm vector store and embeddings cache."""
        logger.info("Initializing vector store index in ChatPipelineService...")
        self.vector_store.initialize_store(force_reload=False)
        logger.info("Vector store initialization complete (%d chunks indexed).", self.vector_store.count())

    async def execute_query(self, user_query: str) -> ChatQueryResponse:
        """Execute end-to-end processing of a user query through all 4 safety & retrieval tiers.

        Args:
            user_query: Natural language question from user.

        Returns:
            Structured ChatQueryResponse with validated facts-only output.
        """
        start_time = time.perf_counter()

        # =========================================================================
        # Tier 1: PII Pre-Retrieval Filter
        # =========================================================================
        pii_result = self.pii_filter.check(user_query)
        if pii_result.is_pii_detected:
            refusal = self.refusal_handler.handle_pii_blocked()
            latency = (time.perf_counter() - start_time) * 1000.0
            return ChatQueryResponse(
                status="blocked",
                query=user_query,
                intent="pii_detected",
                response=refusal.response,
                sentence_count=refusal.sentence_count,
                source_url=refusal.source_url,
                last_updated=refusal.last_updated,
                disclaimer=self.settings.default_disclaimer,
                is_fallback=False,
                latency_ms=round(latency, 2),
            )

        # =========================================================================
        # Tier 2: Intent Classification & Safety Routing
        # =========================================================================
        intent_result = self.intent_router.classify(user_query)
        if intent_result.is_blocked:
            if intent_result.intent == QueryIntent.ADVISORY:
                refusal = self.refusal_handler.handle_advisory()
            elif intent_result.intent == QueryIntent.COMPARISON:
                refusal = self.refusal_handler.handle_comparison()
            elif intent_result.intent == QueryIntent.PERFORMANCE_CALC:
                refusal = self.refusal_handler.handle_performance_calc()
            elif intent_result.intent == QueryIntent.LIVE_NAV_PRICE:
                refusal = self.refusal_handler.handle_live_nav()
            elif intent_result.intent == QueryIntent.PROMPT_INJECTION:
                refusal = self.refusal_handler.handle_prompt_injection()
            else:
                refusal = self.refusal_handler.handle_advisory()

            latency = (time.perf_counter() - start_time) * 1000.0
            return ChatQueryResponse(
                status="refusal",
                query=user_query,
                intent=intent_result.intent.value,
                response=refusal.response,
                sentence_count=refusal.sentence_count,
                source_url=refusal.source_url,
                last_updated=refusal.last_updated,
                disclaimer=self.settings.default_disclaimer,
                is_fallback=False,
                latency_ms=round(latency, 2),
            )

        # =========================================================================
        # Tier 3: Two-Stage Entity-Filtered Retrieval
        # =========================================================================
        target_query = intent_result.factual_subquery or user_query
        retrieval_result = self.retriever.retrieve(target_query)

        # Handle Ambiguous Scheme (e.g. "What is the exit load?" without scheme)
        if retrieval_result.status == ResolutionStatus.AMBIGUOUS_SCHEME:
            refusal = self.refusal_handler.handle_ambiguous_scheme(
                parameter=retrieval_result.resolved_entity.parameter
            )
            latency = (time.perf_counter() - start_time) * 1000.0
            return ChatQueryResponse(
                status="disambiguation",
                query=user_query,
                intent="ambiguous_scheme",
                response=refusal.response,
                sentence_count=refusal.sentence_count,
                source_url=refusal.source_url,
                last_updated=refusal.last_updated,
                disclaimer=self.settings.default_disclaimer,
                is_fallback=False,
                latency_ms=round(latency, 2),
            )

        # Handle Out-of-Scope Scheme (e.g. "SBI Bluechip")
        if retrieval_result.status == ResolutionStatus.OUT_OF_SCOPE:
            refusal = self.refusal_handler.handle_out_of_scope(
                out_of_scope_name=retrieval_result.resolved_entity.out_of_scope_name
            )
            latency = (time.perf_counter() - start_time) * 1000.0
            return ChatQueryResponse(
                status="refusal",
                query=user_query,
                intent="out_of_scope",
                response=refusal.response,
                sentence_count=refusal.sentence_count,
                source_url=refusal.source_url,
                last_updated=refusal.last_updated,
                disclaimer=self.settings.default_disclaimer,
                is_fallback=False,
                latency_ms=round(latency, 2),
            )

        if not retrieval_result.primary_chunk:
            refusal = self.refusal_handler.handle_out_of_scope()
            latency = (time.perf_counter() - start_time) * 1000.0
            return ChatQueryResponse(
                status="refusal",
                query=user_query,
                intent="no_match",
                response=refusal.response,
                sentence_count=refusal.sentence_count,
                source_url=refusal.source_url,
                last_updated=refusal.last_updated,
                disclaimer=self.settings.default_disclaimer,
                is_fallback=False,
                latency_ms=round(latency, 2),
            )

        chunk = retrieval_result.primary_chunk

        # =========================================================================
        # Tier 4: Constrained Grounded Generation & Validation
        # =========================================================================
        gen_input = GenerationInput(
            query=user_query,
            chunk_content=chunk.content,
            canonical_url=retrieval_result.official_source_url,
            last_updated=retrieval_result.last_updated,
            requires_disclaimer=intent_result.requires_disclaimer,
        )

        gen_result = await self.generator.generate(gen_input)
        latency = (time.perf_counter() - start_time) * 1000.0

        return ChatQueryResponse(
            status="success",
            query=user_query,
            intent=intent_result.intent.value,
            response=gen_result.response,
            sentence_count=gen_result.sentence_count,
            source_url=gen_result.source_url,
            last_updated=gen_result.last_updated,
            disclaimer=self.settings.default_disclaimer if intent_result.requires_disclaimer else None,
            is_fallback=gen_result.is_fallback,
            latency_ms=round(latency, 2),
        )

    def get_supported_schemes(self) -> List[SchemeSummary]:
        """Load and return summary metadata for all 5 supported HDFC schemes."""
        schemes_path = self.settings.absolute_data_source_path
        if not schemes_path.exists():
            schemes_path = PROJECT_ROOT / "data" / "processed" / "schemes.json"

        if not schemes_path.exists():
            return []

        try:
            with open(schemes_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            summaries: List[SchemeSummary] = []
            for item in data.get("schemes", []):
                summaries.append(
                    SchemeSummary(
                        scheme_code=item.get("scheme_code", ""),
                        scheme_name=item.get("scheme_name", ""),
                        category=item.get("category", ""),
                        benchmark_index=item.get("benchmark_index", ""),
                        riskometer=item.get("riskometer", ""),
                        source_url=item.get("official_source_url", ""),
                    )
                )
            return summaries
        except Exception as e:
            logger.error("Failed to load schemes metadata: %s", e)
            return []

    def get_health_metrics(self) -> Dict[str, Any]:
        """Return diagnostic health and rate limiter metrics."""
        count = self.vector_store.count()
        rate_metrics = self.generator.rate_limiter.get_metrics()

        return {
            "status": "healthy" if count > 0 else "degraded",
            "app": self.settings.app_name,
            "version": self.settings.app_version,
            "environment": self.settings.environment,
            "vector_store_initialized": count > 0,
            "total_indexed_chunks": count,
            "rate_limiter": rate_metrics,
        }
