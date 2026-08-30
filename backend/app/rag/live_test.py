"""Quick live interactive testing utility for Mutual Fund FAQ Assistant RAG pipeline."""

import asyncio
import os
import sys

from backend.app.core.config import get_settings
from backend.app.guardrails.intent_router import IntentRouter
from backend.app.guardrails.pii_filter import PIIFilter
from backend.app.guardrails.refusal_handler import RefusalHandler
from backend.app.rag.generator import GroundedGenerator
from backend.app.rag.retriever import SchemeFilteredRetriever
from backend.app.rag.vector_store import VectorStoreService
from backend.app.schemas.generation import GenerationInput
from backend.app.schemas.guardrails import QueryIntent
from backend.app.schemas.retrieval import ResolutionStatus


async def run_live_query(user_query: str) -> None:
    """Execute complete end-to-end pipeline on a user query."""
    settings = get_settings()
    print("=" * 70)
    print(f"QUERY: {user_query}")
    print(f"MODEL: {settings.groq_model}")
    print(f"GROQ KEY PRESENT: {bool(settings.groq_api_key and settings.groq_api_key != 'your_groq_api_key_here')}")
    print("=" * 70)

    # 1. PII Check
    pii_filter = PIIFilter()
    pii_result = pii_filter.check(user_query)
    if pii_result.is_pii_detected:
        refusal = RefusalHandler().handle_pii_blocked()
        print("\n[GUARDRAIL BLOCKED: PII DETECTED]")
        print(refusal.response)
        print(f"\nSource: {refusal.source_url}")
        print(f"Last updated from sources: {refusal.last_updated}")
        return

    # 2. Intent Routing
    router = IntentRouter()
    intent_result = router.classify(user_query)
    if intent_result.is_blocked:
        refusal_handler = RefusalHandler()
        if intent_result.intent == QueryIntent.ADVISORY:
            refusal = refusal_handler.handle_advisory()
        elif intent_result.intent == QueryIntent.COMPARISON:
            refusal = refusal_handler.handle_comparison()
        elif intent_result.intent == QueryIntent.PERFORMANCE_CALC:
            refusal = refusal_handler.handle_performance_calc()
        elif intent_result.intent == QueryIntent.LIVE_NAV_PRICE:
            refusal = refusal_handler.handle_live_nav()
        elif intent_result.intent == QueryIntent.PROMPT_INJECTION:
            refusal = refusal_handler.handle_prompt_injection()
        else:
            refusal = refusal_handler.handle_advisory()

        print(f"\n[GUARDRAIL REFUSAL: {intent_result.intent.value.upper()}]")
        print(refusal.response)
        print(f"\nSource: {refusal.source_url}")
        print(f"Last updated from sources: {refusal.last_updated}")
        return

    # 3. Two-Stage Retrieval
    vector_store = VectorStoreService()
    vector_store.initialize_store(force_reload=False)
    retriever = SchemeFilteredRetriever(vector_store=vector_store)
    
    target_query = intent_result.factual_subquery or user_query
    retrieval_result = retriever.retrieve(target_query)

    if retrieval_result.status == ResolutionStatus.AMBIGUOUS_SCHEME:
        refusal = RefusalHandler().handle_ambiguous_scheme(parameter=retrieval_result.resolved_entity.parameter)
        print("\n[AMBIGUOUS SCHEME]")
        print(refusal.response)
        print(f"\nSource: {refusal.source_url}")
        print(f"Last updated from sources: {refusal.last_updated}")
        return

    if retrieval_result.status == ResolutionStatus.OUT_OF_SCOPE:
        refusal = RefusalHandler().handle_out_of_scope(out_of_scope_name=retrieval_result.resolved_entity.out_of_scope_name)
        print("\n[OUT OF SCOPE SCHEME]")
        print(refusal.response)
        print(f"\nSource: {refusal.source_url}")
        print(f"Last updated from sources: {refusal.last_updated}")
        return

    if not retrieval_result.primary_chunk:
        print("\n[NO CHUNK RETRIEVED]")
        return

    chunk = retrieval_result.primary_chunk
    print(f"\n[RETRIEVED CHUNK: {chunk.chunk_id}] (Score: {chunk.similarity_score})")
    print(f"Content: {chunk.content}")

    # 4. Grounded Generation
    generator = GroundedGenerator()
    gen_input = GenerationInput(
        query=user_query,
        chunk_content=chunk.content,
        canonical_url=retrieval_result.official_source_url,
        last_updated=retrieval_result.last_updated,
        requires_disclaimer=intent_result.requires_disclaimer,
    )

    result = await generator.generate(gen_input)
    print("\n" + "-" * 70)
    print(f"FINAL RESPONSE (Mode: {result.model}, Sentences: {result.sentence_count}, Latency: {result.latency_ms}ms):")
    print("-" * 70)
    print(result.response)
    print("=" * 70)


if __name__ == "__main__":
    sample_query = sys.argv[1] if len(sys.argv) > 1 else "What is the exit load for HDFC Small Cap Fund?"
    asyncio.run(run_live_query(sample_query))
