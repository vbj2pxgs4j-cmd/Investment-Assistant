"""Unit and integration tests for FastAPI REST API endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient

from backend.main import app


@pytest.fixture
async def async_client():
    """Provide AsyncClient against the FastAPI application."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.mark.asyncio
async def test_root_endpoint(async_client: AsyncClient):
    """Verify root endpoint returns online status and metadata."""
    response = await async_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert "Mutual Fund FAQ Assistant" in data["app"]
    assert "disclaimer" in data


@pytest.mark.asyncio
async def test_health_endpoint(async_client: AsyncClient):
    """Verify /api/v1/health returns system status and vector index readiness."""
    response = await async_client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] in ["healthy", "degraded"]
    assert "version" in data
    assert "rate_limiter" in data
    assert data["rate_limiter"]["rpm_limit"] == 30
    assert data["rate_limiter"]["tpm_limit"] == 8000


@pytest.mark.asyncio
async def test_schemes_endpoint(async_client: AsyncClient):
    """Verify /api/v1/schemes returns all 5 curated HDFC Mutual Fund schemes."""
    response = await async_client.get("/api/v1/schemes")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 5
    assert len(data["schemes"]) == 5

    scheme_names = [s["scheme_name"] for s in data["schemes"]]
    assert "HDFC Mid-Cap Opportunities Fund" in scheme_names
    assert "HDFC Small Cap Fund" in scheme_names
    assert "HDFC ELSS Tax Saver Fund" in scheme_names
    assert "HDFC Gold ETF Fund of Fund" in scheme_names
    assert "HDFC Top 100 / Large Cap Fund" in scheme_names


@pytest.mark.asyncio
async def test_rate_limit_telemetry_endpoint(async_client: AsyncClient):
    """Verify /api/v1/rate-limit returns live telemetry quotas."""
    response = await async_client.get("/api/v1/rate-limit")
    assert response.status_code == 200
    data = response.json()
    assert data["rpm_limit"] == 30
    assert data["rpd_limit"] == 1000
    assert data["tpm_limit"] == 8000
    assert data["tpd_limit"] == 200000


@pytest.mark.asyncio
async def test_chat_query_factual(async_client: AsyncClient):
    """Verify /api/v1/chat/query answers factual questions conforming to ≤ 3 sentences."""
    payload = {"query": "What is the exit load for HDFC Small Cap Fund?"}
    response = await async_client.post("/api/v1/chat/query", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "success"
    assert data["sentence_count"] <= 3
    assert data["sentence_count"] >= 1
    assert "groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth" in data["source_url"]
    assert "Last updated from sources: 2024-04-01" in data["response"]
    assert data["latency_ms"] > 0


@pytest.mark.asyncio
async def test_chat_query_pii_interception(async_client: AsyncClient):
    """Verify /api/v1/chat/query intercepts queries containing PAN or PII."""
    payload = {"query": "My PAN is ABCDE1234F, tell me my SIP status for HDFC Mid Cap"}
    response = await async_client.post("/api/v1/chat/query", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "blocked"
    assert data["intent"] == "pii_detected"
    assert "ABCDE1234F" not in data["response"]
    assert "PII" in data["response"] or "personal" in data["response"].lower()


@pytest.mark.asyncio
async def test_chat_query_advisory_refusal(async_client: AsyncClient):
    """Verify /api/v1/chat/query refuses investment advisory prompts."""
    payload = {"query": "Should I invest in HDFC Mid-Cap Opportunities Fund?"}
    response = await async_client.post("/api/v1/chat/query", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "refusal"
    assert data["intent"] == "advisory"
    assert data["sentence_count"] <= 3
    assert "https://groww.in/mutual-funds" in data["source_url"]


@pytest.mark.asyncio
async def test_chat_query_comparison_refusal(async_client: AsyncClient):
    """Verify /api/v1/chat/query refuses comparative advice."""
    payload = {"query": "Which is better HDFC Small Cap or HDFC Mid Cap?"}
    response = await async_client.post("/api/v1/chat/query", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "refusal"
    assert data["intent"] == "comparison"
    assert data["sentence_count"] <= 3


@pytest.mark.asyncio
async def test_chat_query_ambiguous_scheme_disambiguation(async_client: AsyncClient):
    """Verify /api/v1/chat/query returns disambiguation when no scheme is mentioned."""
    payload = {"query": "What is the minimum SIP amount?"}
    response = await async_client.post("/api/v1/chat/query", json=payload)
    assert response.status_code == 200
    data = response.json()

    assert data["status"] == "disambiguation"
    assert data["intent"] == "ambiguous_scheme"
    assert data["sentence_count"] <= 3
    assert "specify which" in data["response"].lower() or "5 supported" in data["response"].lower()


@pytest.mark.asyncio
async def test_chat_query_validation_error(async_client: AsyncClient):
    """Verify /api/v1/chat/query returns 422 Unprocessable Entity for invalid or empty queries."""
    # Blank string
    response = await async_client.post("/api/v1/chat/query", json={"query": "   "})
    assert response.status_code == 422
    data = response.json()
    assert data["error_type"] == "validation_error"

    # Missing query field
    response_missing = await async_client.post("/api/v1/chat/query", json={})
    assert response_missing.status_code == 422
