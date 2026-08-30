"""Pydantic schemas for LLM text synthesis, generation inputs, and validated outputs."""

from typing import Optional
from pydantic import BaseModel, Field


class GenerationInput(BaseModel):
    """Input payload for grounded factual response synthesis."""
    query: str = Field(description="User query string")
    chunk_content: str = Field(description="Grounded factual knowledge chunk content")
    scheme_name: str = Field(default="", description="Official scheme name or operational scope")
    category: str = Field(default="", description="SEBI category classification")
    parameter: str = Field(default="", description="Factual parameter domain")
    canonical_url: str = Field(
        default="https://groww.in/mutual-funds",
        description="Authoritative whitelisted Groww URL citation"
    )
    last_updated: str = Field(
        default="2024-04-01",
        description="Last updated date string in YYYY-MM-DD format"
    )
    requires_disclaimer: bool = Field(
        default=False,
        description="True if an additional non-advisory disclaimer is required"
    )


class GenerationResult(BaseModel):
    """Validated, formatted, and constrained factual response output."""
    response: str = Field(
        description="The final validated factual answer strictly adhering to sentence constraints"
    )
    raw_llm_output: Optional[str] = Field(
        default=None,
        description="Raw unmodified output returned from the LLM engine"
    )
    model: str = Field(
        default="openai/gpt-oss-120b",
        description="Name of the model utilized for synthesis"
    )
    sentence_count: int = Field(
        description="Calculated sentence count of the final answer (strictly <= 3)"
    )
    source_url: str = Field(
        description="Verified canonical Groww URL citation"
    )
    last_updated: str = Field(
        description="Source last updated date footer value"
    )
    disclaimer: str = Field(
        default="Facts-only. No investment advice.",
        description="Mandatory compliance disclaimer"
    )
    is_fallback: bool = Field(
        default=False,
        description="True if response was generated via local deterministic fallback engine"
    )
    latency_ms: float = Field(
        default=0.0,
        description="Total synthesis and validation latency in milliseconds"
    )
