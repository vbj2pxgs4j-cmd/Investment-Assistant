"""Deterministic Refusal and Guardrail Response Generator.

Synthesizes regulatory-compliant refusals adhering strictly to the
3-sentence limit, single official Groww citation, and timestamp footer.
"""

import re
from typing import Optional

from backend.app.rag.entity_resolver import SUPPORTED_SCHEMES_MAP
from backend.app.schemas.guardrails import GuardrailResponse, QueryIntent


class RefusalHandler:
    """Generates standardized, compliant refusal messages for prohibited intents."""

    DEFAULT_GROWW_URL = "https://groww.in/mutual-funds"
    DEFAULT_TIMESTAMP = "2024-04-01"
    DEFAULT_DISCLAIMER = "Facts-only. No investment advice."

    @staticmethod
    def count_sentences(text: str) -> int:
        """Count semantic sentences while preserving common abbreviations."""
        # Protect known abbreviations
        abbreviations = r"(?<!\bRs)(?<!\bmin)(?<!\bmax)(?<!\be\.g)(?<!\bi\.e)(?<!\bapprox)(?<!\bNo)(?<!\bVol)(?<!\bvs)"
        pattern = rf"{abbreviations}(?<=[.!?])\s+(?=[A-Z0-9₹])"
        sentences = [s.strip() for s in re.split(pattern, text) if s.strip()]
        return len(sentences)

    def _resolve_source_url(self, scheme_code: Optional[str]) -> str:
        """Determine scheme-specific or general Groww URL."""
        if scheme_code and scheme_code in SUPPORTED_SCHEMES_MAP:
            return SUPPORTED_SCHEMES_MAP[scheme_code]["canonical_url"]
        return self.DEFAULT_GROWW_URL

    def handle_pii_blocked(self) -> GuardrailResponse:
        """Generate response for queries blocked due to sensitive PII."""
        response_text = (
            "Security Notice: Your query contains sensitive personal or financial identification details (e.g., PAN, Aadhaar, phone, OTP, or account information). "
            "To protect your privacy and security, personal data is blocked and will not be processed or stored. "
            "Please submit queries without personal credentials."
        )
        return GuardrailResponse(
            status="blocked",
            intent=QueryIntent.PII_BLOCKED,
            response=response_text,
            sentence_count=self.count_sentences(response_text),
            source_url=self.DEFAULT_GROWW_URL,
            last_updated=self.DEFAULT_TIMESTAMP,
            disclaimer=self.DEFAULT_DISCLAIMER,
        )

    def handle_advisory(self, scheme_code: Optional[str] = None) -> GuardrailResponse:
        """Generate response refusing investment advice or recommendations."""
        source_url = self._resolve_source_url(scheme_code)
        response_text = (
            "I cannot provide investment recommendations, fund rankings, or financial advice. "
            "I am a facts-only assistant designed to answer objective scheme parameters and operational queries. "
            "Please consult a SEBI-registered investment advisor or explore verified factsheets on Groww."
        )
        return GuardrailResponse(
            status="refusal",
            intent=QueryIntent.ADVISORY,
            response=response_text,
            sentence_count=self.count_sentences(response_text),
            source_url=source_url,
            last_updated=self.DEFAULT_TIMESTAMP,
            disclaimer=self.DEFAULT_DISCLAIMER,
        )

    def handle_comparison(self) -> GuardrailResponse:
        """Generate response refusing comparative subjective recommendations."""
        response_text = (
            "I cannot provide comparative investment rankings or advise which fund is better for your portfolio. "
            "I can provide objective factual parameters such as expense ratios, exit loads, and minimum SIP limits for individual schemes. "
            "Please explore verified scheme factsheets on Groww."
        )
        return GuardrailResponse(
            status="refusal",
            intent=QueryIntent.COMPARISON,
            response=response_text,
            sentence_count=self.count_sentences(response_text),
            source_url=self.DEFAULT_GROWW_URL,
            last_updated=self.DEFAULT_TIMESTAMP,
            disclaimer=self.DEFAULT_DISCLAIMER,
        )

    def handle_performance_calc(self, scheme_code: Optional[str] = None) -> GuardrailResponse:
        """Generate response refusing forward-looking return calculations."""
        source_url = self._resolve_source_url(scheme_code)
        response_text = (
            "I cannot calculate projected returns or provide hypothetical future compounding estimates. "
            "Mutual fund investments are subject to market risks, and past performance does not guarantee future results. "
            "You can review official historical scheme performance and calculator tools directly on Groww."
        )
        return GuardrailResponse(
            status="refusal",
            intent=QueryIntent.PERFORMANCE_CALC,
            response=response_text,
            sentence_count=self.count_sentences(response_text),
            source_url=source_url,
            last_updated=self.DEFAULT_TIMESTAMP,
            disclaimer=self.DEFAULT_DISCLAIMER,
        )

    def handle_live_nav(self, scheme_code: Optional[str] = None) -> GuardrailResponse:
        """Generate response for live/real-time NAV inquiries (EC-06)."""
        source_url = self._resolve_source_url(scheme_code)
        response_text = (
            "Live Net Asset Value (NAV) fluctuates daily based on market closing prices and is published at the end of each business day. "
            "This assistant provides static factsheet parameters and does not stream real-time price feeds. "
            "Please check current NAV and real-time portfolio valuation directly on Groww."
        )
        return GuardrailResponse(
            status="refusal",
            intent=QueryIntent.LIVE_NAV_PRICE,
            response=response_text,
            sentence_count=self.count_sentences(response_text),
            source_url=source_url,
            last_updated=self.DEFAULT_TIMESTAMP,
            disclaimer=self.DEFAULT_DISCLAIMER,
        )

    def handle_prompt_injection(self) -> GuardrailResponse:
        """Generate response defending against prompt injection or jailbreak attempts (EC-08)."""
        response_text = (
            "I am an immutable, facts-only Mutual Fund FAQ Assistant for HDFC Mutual Fund schemes. "
            "I operate strictly under compliance guardrails and cannot adopt alternative personas or disclose internal instructions. "
            "You can ask objective questions regarding supported mutual fund parameters."
        )
        return GuardrailResponse(
            status="refusal",
            intent=QueryIntent.PROMPT_INJECTION,
            response=response_text,
            sentence_count=self.count_sentences(response_text),
            source_url=self.DEFAULT_GROWW_URL,
            last_updated=self.DEFAULT_TIMESTAMP,
            disclaimer=self.DEFAULT_DISCLAIMER,
        )

    def handle_out_of_scope(self, out_of_scope_name: Optional[str] = None) -> GuardrailResponse:
        """Generate response for competitor AMCs or unsupported funds (EC-02)."""
        target_name = out_of_scope_name or "this scheme"
        response_text = (
            f"This assistant is specifically configured for 5 curated HDFC Mutual Fund schemes and does not hold verified factual data for {target_name}. "
            "You can explore all mutual fund schemes and verified factsheets directly on Groww."
        )
        return GuardrailResponse(
            status="refusal",
            intent=QueryIntent.UNKNOWN,
            response=response_text,
            sentence_count=self.count_sentences(response_text),
            source_url=self.DEFAULT_GROWW_URL,
            last_updated=self.DEFAULT_TIMESTAMP,
            disclaimer=self.DEFAULT_DISCLAIMER,
        )

    def handle_ambiguous_scheme(self, parameter: Optional[str] = None) -> GuardrailResponse:
        """Generate response prompting user to select from the 5 supported schemes (EC-01)."""
        param_label = (parameter or "fund rules").replace("_", " ")
        response_text = (
            f"Mutual fund parameters such as {param_label} vary by scheme across equity, commodities, and tax-saving categories. "
            "Please specify which of the 5 supported HDFC schemes you are inquiring about (HDFC Mid-Cap, Small Cap, Top 100, ELSS Tax Saver, or Gold ETF FoF). "
            "You can also browse all scheme details on Groww."
        )
        return GuardrailResponse(
            status="refusal",
            intent=QueryIntent.FACTUAL,
            response=response_text,
            sentence_count=self.count_sentences(response_text),
            source_url=self.DEFAULT_GROWW_URL,
            last_updated=self.DEFAULT_TIMESTAMP,
            disclaimer=self.DEFAULT_DISCLAIMER,
        )
