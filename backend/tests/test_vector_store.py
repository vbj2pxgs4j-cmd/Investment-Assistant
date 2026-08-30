"""Unit tests for ChromaDB Vector Store Service and indexing engine."""

import pytest
from pathlib import Path

from backend.app.rag.vector_store import VectorStoreService


@pytest.fixture(scope="module")
def vector_store() -> VectorStoreService:
    store = VectorStoreService()
    store.initialize_store(force_reload=False)
    return store


def test_vector_store_initialization_and_count(vector_store: VectorStoreService):
    """Verify that vector store initializes with all 38 chunks."""
    total_docs = vector_store.count()
    assert total_docs == 38, f"Expected 38 documents, found {total_docs}"


def test_vector_store_metadata_filtered_query(vector_store: VectorStoreService):
    """Verify that metadata filtering constrains results strictly to the specified scheme."""
    scheme_code = "hdfc-mid-cap-fund-direct-growth"
    results = vector_store.query(
        query_text="What is the exit load?",
        n_results=5,
        where={"scheme_code": scheme_code},
    )

    assert len(results) > 0
    for res in results:
        meta = res["metadata"]
        assert meta["scheme_code"] == scheme_code
        assert meta["official_source_url"] == "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth"
        assert res["similarity_score"] >= 0.0
        assert res["similarity_score"] <= 1.0


def test_vector_store_get_by_id(vector_store: VectorStoreService):
    """Verify direct chunk retrieval by chunk_id."""
    chunk_id = "hdfc_elss_tax_saver_fund_direct_plan_growth_lock_in_period"
    chunk = vector_store.get_chunk_by_id(chunk_id)

    assert chunk is not None
    assert chunk["chunk_id"] == chunk_id
    assert "3" in chunk["content"] or "lock-in" in chunk["content"].lower()
    assert chunk["metadata"]["scheme_code"] == "hdfc-elss-tax-saver-fund-direct-plan-growth"


def test_vector_store_general_operations_chunks(vector_store: VectorStoreService):
    """Verify that general operations chunks are retrievable."""
    results = vector_store.query(
        query_text="how to download account statement",
        n_results=3,
        where={"scheme_code": "general-operations"},
    )

    assert len(results) > 0
    assert results[0]["metadata"]["scheme_code"] == "general-operations"
    assert "groww.in" in results[0]["metadata"]["official_source_url"]
