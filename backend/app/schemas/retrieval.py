"""Pydantic schemas for query resolution, entity classification, and retrieval outputs."""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ResolutionStatus(str, Enum):
    """Status classification of entity and scheme resolution."""
    RESOLVED = "resolved"
    AMBIGUOUS_SCHEME = "ambiguous_scheme"
    OUT_OF_SCOPE = "out_of_scope"
    GENERAL_OPERATIONS = "general_operations"
    UNKNOWN = "unknown"


class ParameterType(str, Enum):
    """Target parameter domains for mutual fund queries."""
    EXPENSE_RATIO = "expense_ratio"
    EXIT_LOAD = "exit_load"
    INVESTMENT_LIMITS = "investment_limits"
    LOCK_IN_PERIOD = "lock_in_period"
    TAXATION = "taxation"
    OPERATIONS = "operations"
    FUND_OVERVIEW = "fund_overview"
    UNKNOWN = "unknown"


class ResolvedEntity(BaseModel):
    """Structured representation of resolved query entities and parameters."""
    status: ResolutionStatus = Field(
        default=ResolutionStatus.UNKNOWN,
        description="Overall resolution classification status"
    )
    scheme_code: Optional[str] = Field(
        default=None,
        description="Canonical scheme code slug (e.g. hdfc-mid-cap-fund-direct-growth)"
    )
    scheme_name: Optional[str] = Field(
        default=None,
        description="Full official scheme name or operational scope"
    )
    parameter: Optional[str] = Field(
        default=None,
        description="String identifier of the parameter domain"
    )
    parameter_type: ParameterType = Field(
        default=ParameterType.UNKNOWN,
        description="Enumerated parameter domain classification"
    )
    is_ambiguous: bool = Field(
        default=False,
        description="True if parameter is identified without any fund entity"
    )
    out_of_scope_name: Optional[str] = Field(
        default=None,
        description="Identified competitor or unsupported fund/AMC name"
    )
    raw_query: str = Field(
        default="",
        description="Original unmodified user query string"
    )
    confidence: float = Field(
        default=0.0,
        description="Confidence score of the entity match [0.0 - 1.0]"
    )
    matched_alias: Optional[str] = Field(
        default=None,
        description="Specific alias keyword or phrase matched in query"
    )


class RetrievedChunk(BaseModel):
    """Factual knowledge chunk returned from the vector retrieval engine."""
    chunk_id: str = Field(description="Unique deterministic chunk ID")
    scheme_code: str = Field(description="Canonical scheme code slug or 'general-operations'")
    scheme_name: str = Field(description="Full official name of scheme")
    category: str = Field(description="SEBI category classification")
    parameter: str = Field(description="Factual parameter domain")
    title: str = Field(description="Descriptive chunk title")
    content: str = Field(description="Factual narrative content text")
    official_source_url: str = Field(description="Whitelisted canonical Groww URL")
    last_updated: str = Field(description="Last updated date in YYYY-MM-DD format")
    similarity_score: float = Field(
        default=0.0,
        description="Dense vector cosine similarity score [0.0 - 1.0]"
    )
    metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Structured numeric and boolean metadata attributes"
    )


class RetrievalResult(BaseModel):
    """Consolidated payload returned by the hybrid filtered retrieval engine."""
    status: ResolutionStatus = Field(
        description="Status of the retrieval execution"
    )
    resolved_entity: ResolvedEntity = Field(
        description="Resolved entity and parameter metadata"
    )
    primary_chunk: Optional[RetrievedChunk] = Field(
        default=None,
        description="Top-1 ranked grounded knowledge chunk"
    )
    candidate_chunks: List[RetrievedChunk] = Field(
        default_factory=list,
        description="Candidate chunks retrieved within similarity threshold"
    )
    official_source_url: str = Field(
        default="https://groww.in/mutual-funds",
        description="Authoritative source URL for citation"
    )
    last_updated: str = Field(
        default="2024-04-01",
        description="Canonical source date footer value"
    )
    ambiguity_message: Optional[str] = Field(
        default=None,
        description="Clarification prompt message when scheme is ambiguous"
    )
    out_of_scope_message: Optional[str] = Field(
        default=None,
        description="Disclaimer message when query pertains to unsupported fund"
    )
    supported_schemes: List[Dict[str, str]] = Field(
        default_factory=list,
        description="List of the 5 curated HDFC schemes for user guidance"
    )
    latency_ms: float = Field(
        default=0.0,
        description="Retrieval execution latency in milliseconds"
    )
