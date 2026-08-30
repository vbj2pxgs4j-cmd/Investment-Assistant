"""Pydantic schemas for atomic parameter-domain knowledge chunks."""

import re
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class KnowledgeChunk(BaseModel):
    """Schema representing an atomic factual knowledge chunk."""
    chunk_id: str = Field(description="Unique deterministic identifier for the chunk")
    scheme_code: str = Field(description="Canonical scheme code slug or 'general-operations'")
    scheme_name: str = Field(description="Full official name of the scheme or operational entity")
    category: str = Field(description="SEBI category classification")
    parameter: str = Field(description="Factual parameter domain (e.g., exit_load, expense_ratio, etc.)")
    title: str = Field(description="Descriptive title of the knowledge chunk")
    content: str = Field(description="Concise, verified factual narrative content")
    official_source_url: str = Field(description="Authoritative whitelisted Groww URL")
    last_updated: str = Field(description="Last updated date in YYYY-MM-DD format")
    keywords: List[str] = Field(default_factory=list, description="Associated search and retrieval keywords")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Structured numerical and categorical metadata")

    @field_validator("official_source_url")
    @classmethod
    def validate_source_url(cls, url: str) -> str:
        """Ensure citation URL is from the whitelisted Groww domain."""
        if not ("groww.in/mutual-funds" in url or "groww.in" in url):
            raise ValueError(f"Invalid official_source_url '{url}'. Must be under groww.in")
        return url

    @field_validator("last_updated")
    @classmethod
    def validate_date_format(cls, val: str) -> str:
        """Ensure date follows YYYY-MM-DD pattern."""
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", val):
            raise ValueError(f"Invalid last_updated date '{val}'. Expected YYYY-MM-DD format.")
        return val


class ChunkCollection(BaseModel):
    """Container schema for collection of all processed knowledge chunks."""
    total_chunks: int = Field(description="Total number of chunks in the corpus")
    last_updated: str = Field(description="Corpus update date in YYYY-MM-DD format")
    chunks: List[KnowledgeChunk] = Field(description="List of all atomic factual chunks")
