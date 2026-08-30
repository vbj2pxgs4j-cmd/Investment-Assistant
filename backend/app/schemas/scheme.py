"""Pydantic schemas for mutual fund schemes and factual parameters."""

import re
from datetime import date
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class LockInPeriod(BaseModel):
    """Schema for scheme lock-in details."""
    has_lock_in: bool = Field(description="Whether the scheme has a mandatory statutory lock-in period")
    duration_years: int = Field(default=0, ge=0, description="Lock-in duration in years (e.g., 3 for ELSS)")
    description: str = Field(description="Factual narrative explaining lock-in condition")


class ExpenseRatio(BaseModel):
    """Schema for scheme Total Expense Ratio (TER)."""
    direct_plan_percentage: float = Field(gt=0.0, le=5.0, description="Direct plan Total Expense Ratio percentage")
    regular_plan_percentage: Optional[float] = Field(default=None, description="Regular plan Total Expense Ratio percentage")
    description: str = Field(description="Factual narrative explaining expense ratio")


class ExitLoad(BaseModel):
    """Schema for scheme exit load structure."""
    percentage: float = Field(ge=0.0, le=10.0, description="Exit load percentage applicable if redeemed early")
    holding_period_threshold_days: int = Field(ge=0, description="Minimum holding period in days to avoid exit load")
    description: str = Field(description="Factual narrative explaining exit load rules")


class InvestmentLimits(BaseModel):
    """Schema for minimum investment thresholds."""
    min_sip_amount: int = Field(gt=0, description="Minimum SIP amount in INR per installment")
    min_lump_sum_amount: int = Field(gt=0, description="Minimum initial lump sum purchase in INR")
    min_additional_investment: int = Field(gt=0, description="Minimum additional investment in INR")
    sip_frequency: str = Field(default="Monthly / Quarterly", description="Allowed SIP frequencies")
    description: str = Field(description="Factual narrative explaining investment limits")


class TaxationInfo(BaseModel):
    """Schema for scheme taxation rules."""
    equity_taxation: bool = Field(description="Whether scheme is taxed as equity fund (holding >65% domestic equities)")
    tax_deduction: Optional[str] = Field(default=None, description="Section 80C tax deduction details if applicable")
    short_term_capital_gains: Optional[str] = Field(default=None, description="Short-term capital gains tax rules")
    long_term_capital_gains: Optional[str] = Field(default=None, description="Long-term capital gains tax rules")
    tax_regime: Optional[str] = Field(default=None, description="Debt/Commodity or Specified Mutual Fund taxation notes")


class OperationsInfo(BaseModel):
    """Schema for operational workflows and statement access."""
    account_statement_procedure: str = Field(description="Steps to download account statements")
    folio_lookup: str = Field(description="Steps to verify or lookup registered folio number")


class SchemeData(BaseModel):
    """Unified schema for a mutual fund scheme factual profile."""
    scheme_name: str = Field(description="Full official name of the scheme")
    scheme_code: str = Field(description="Unique canonical identifier / slug matching Groww URL")
    plan_type: str = Field(default="Direct Plan - Growth Option", description="Plan type and option")
    amc: str = Field(default="HDFC Asset Management Company Limited", description="Asset Management Company")
    category: str = Field(description="SEBI category classification (e.g., Equity: Mid Cap)")
    fund_type: str = Field(description="Broad description of fund structure and objective")
    benchmark_index: str = Field(description="Primary benchmark index (e.g., NIFTY Midcap 150 TRI)")
    riskometer: str = Field(description="SEBI Riskometer rating (e.g., Very High, High)")
    lock_in_period: LockInPeriod
    expense_ratio: ExpenseRatio
    exit_load: ExitLoad
    investment_limits: InvestmentLimits
    taxation: TaxationInfo
    operations: OperationsInfo
    official_source_url: str = Field(description="Whitelisted Groww scheme URL")
    last_updated: str = Field(description="Source data last updated timestamp in YYYY-MM-DD format")

    @field_validator("official_source_url")
    @classmethod
    def validate_source_url(cls, url: str) -> str:
        """Ensure citation URL is from the whitelisted Groww domain."""
        if not (url.startswith("https://groww.in/mutual-funds") or url.startswith("http://groww.in/mutual-funds")):
            raise ValueError(f"Invalid official_source_url '{url}'. Must start with https://groww.in/mutual-funds")
        return url

    @field_validator("last_updated")
    @classmethod
    def validate_date_format(cls, val: str) -> str:
        """Ensure date follows YYYY-MM-DD pattern."""
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", val):
            raise ValueError(f"Invalid last_updated date '{val}'. Expected YYYY-MM-DD format.")
        return val


class GeneralOperationsData(BaseModel):
    """Schema for general mutual fund operational procedures and educational resources."""
    entity_name: str
    category: str
    statement_download: Dict[str, str]
    capital_gains_report: Dict[str, str]
    educational_resources: Dict[str, str]
    official_source_url: str
    last_updated: str

    @field_validator("official_source_url")
    @classmethod
    def validate_source_url(cls, url: str) -> str:
        if not ("groww.in/mutual-funds" in url or "groww.in" in url):
            raise ValueError(f"Invalid official_source_url '{url}'. Must be under groww.in")
        return url


class ProcessedCorpus(BaseModel):
    """Unified container for all processed schemes and operational records."""
    amc: str = Field(default="HDFC Asset Management Company Limited")
    total_schemes: int
    last_updated: str
    schemes: List[SchemeData]
    general_operations: GeneralOperationsData
