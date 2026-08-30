"""Chat and API payload schemas for REST endpoints."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class ChatQueryRequest(BaseModel):
    """Incoming user chat query request payload."""

    query: str = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="Raw natural language question regarding HDFC Mutual Fund schemes",
        examples=["What is the exit load for HDFC Small Cap Fund?"],
    )
    session_id: Optional[str] = Field(
        default=None,
        max_length=100,
        description="Optional client session identifier",
    )

    @field_validator("query")
    @classmethod
    def validate_query_not_blank(cls, value: str) -> str:
        """Validate query is non-empty after stripping surrounding whitespace."""
        stripped = value.strip()
        if not stripped:
            raise ValueError("Query string cannot be empty or contain only whitespace.")
        return stripped


class ChatQueryResponse(BaseModel):
    """Structured response payload returned by the Facts-Only Assistant."""

    status: str = Field(
        ...,
        description="Execution status: 'success', 'refusal', 'blocked', or 'disambiguation'",
    )
    query: str = Field(
        ...,
        description="The original user query",
    )
    intent: str = Field(
        ...,
        description="Classified query intent (e.g. 'factual', 'advisory', 'pii_detected')",
    )
    response: str = Field(
        ...,
        description="Validated facts-only response text (≤ 3 sentences with citation and footer)",
    )
    sentence_count: int = Field(
        ...,
        ge=0,
        le=3,
        description="Number of sentences in the core answer body",
    )
    source_url: str = Field(
        ...,
        description="Whitelisted Groww source citation URL",
    )
    last_updated: str = Field(
        ...,
        description="Date when source data was last updated (YYYY-MM-DD)",
    )
    disclaimer: Optional[str] = Field(
        default=None,
        description="Compliance disclaimer if required or applicable",
    )
    is_fallback: bool = Field(
        default=False,
        description="True if response was synthesized via deterministic fallback engine",
    )
    latency_ms: float = Field(
        ...,
        description="Total end-to-end request processing time in milliseconds",
    )


class SchemeSummary(BaseModel):
    """Summary of a supported HDFC Mutual Fund scheme."""

    scheme_code: str = Field(..., description="Canonical URL-friendly scheme identifier")
    scheme_name: str = Field(..., description="Full official scheme name")
    category: str = Field(..., description="SEBI category")
    benchmark_index: str = Field(..., description="Benchmark index")
    riskometer: str = Field(..., description="SEBI risk rating")
    source_url: str = Field(..., description="Groww scheme reference URL")


class SchemeListResponse(BaseModel):
    """List of all supported HDFC schemes."""

    total: int = Field(..., description="Total number of supported schemes in the corpus")
    schemes: List[SchemeSummary] = Field(..., description="List of supported scheme summaries")


class HealthResponse(BaseModel):
    """System health check and readiness status."""

    status: str = Field(..., description="Service health: 'healthy' or 'degraded'")
    app: str = Field(..., description="Application name")
    version: str = Field(..., description="Application version")
    environment: str = Field(..., description="Deployment environment")
    vector_store_initialized: bool = Field(..., description="Whether vector index is ready")
    total_indexed_chunks: int = Field(..., description="Number of indexed knowledge chunks")
    rate_limiter: Dict[str, Any] = Field(..., description="Groq RPM/TPM/RPD usage metrics")


class ErrorResponse(BaseModel):
    """Standardized error response model."""

    detail: str = Field(..., description="Error message description")
    error_type: str = Field(..., description="Category of error encountered")
