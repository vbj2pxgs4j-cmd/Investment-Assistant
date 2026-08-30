"""Pydantic schemas for PII safety, intent classification, policy routing, and guardrail responses."""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field


class QueryIntent(str, Enum):
    """Classification of user query intent."""
    FACTUAL = "factual"
    ADVISORY = "advisory"
    COMPARISON = "comparison"
    PERFORMANCE_CALC = "performance_calc"
    LIVE_NAV_PRICE = "live_nav_price"
    PROMPT_INJECTION = "prompt_injection"
    PII_BLOCKED = "pii_blocked"
    MIXED_INTENT = "mixed_intent"
    UNKNOWN = "unknown"


class PIIType(str, Enum):
    """Types of sensitive personal identifiable information."""
    PAN = "pan"
    AADHAAR = "aadhaar"
    PHONE = "phone"
    EMAIL = "email"
    OTP = "otp"
    BANK_ACCOUNT = "bank_account"


class PIICheckResult(BaseModel):
    """Result of PII regex detection and sanitization scan."""
    is_pii_detected: bool = Field(
        default=False,
        description="True if sensitive financial or personal PII was detected"
    )
    detected_types: List[PIIType] = Field(
        default_factory=list,
        description="List of identified PII categories"
    )
    masked_query: str = Field(
        default="",
        description="Sanitized version of the query with PII tokens replaced"
    )
    security_message: Optional[str] = Field(
        default=None,
        description="Security alert message informing user of data block"
    )


class IntentClassificationResult(BaseModel):
    """Result of policy routing and intent classification."""
    intent: QueryIntent = Field(
        default=QueryIntent.FACTUAL,
        description="Classified query intent category"
    )
    is_blocked: bool = Field(
        default=False,
        description="True if query violates compliance rules and must be refused"
    )
    matched_patterns: List[str] = Field(
        default_factory=list,
        description="Specific keyword/regex triggers matched in the query"
    )
    confidence: float = Field(
        default=1.0,
        description="Classification confidence score [0.0 - 1.0]"
    )
    factual_subquery: Optional[str] = Field(
        default=None,
        description="Extracted factual component for mixed-intent queries"
    )
    requires_disclaimer: bool = Field(
        default=False,
        description="True if response requires an additional non-advisory disclaimer"
    )


class GuardrailResponse(BaseModel):
    """Standardized deterministic response payload returned by guardrail refusals."""
    status: str = Field(
        default="refusal",
        description="Status flag ('refusal' or 'blocked')"
    )
    intent: QueryIntent = Field(
        description="The classified intent that triggered this response"
    )
    response: str = Field(
        description="Compliant factual or refusal text strictly adhering to sentence constraints"
    )
    sentence_count: int = Field(
        description="Calculated sentence count of the response (strictly <= 3)"
    )
    source_url: str = Field(
        default="https://groww.in/mutual-funds",
        description="Verified whitelisted Groww URL citation"
    )
    last_updated: str = Field(
        default="2024-04-01",
        description="Canonical source date footer value"
    )
    disclaimer: str = Field(
        default="Facts-only. No investment advice.",
        description="Mandatory compliance disclaimer"
    )
