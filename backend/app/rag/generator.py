"""Constrained Grounded Generator using Groq (openai/gpt-oss-120b) and OutputValidator.

Synthesizes factual answers strictly bounded to retrieved context with zero temperature
and client-side quota management (30 RPM, 1K RPD, 8K TPM, 200K TPD) with instant
deterministic fallback resilience during rate limits or external API degradation.
"""

import logging
import time
from typing import Optional

from groq import AsyncGroq, RateLimitError

from backend.app.core.config import get_settings
from backend.app.guardrails.output_validator import OutputValidator
from backend.app.rag.rate_limiter import GroqRateLimiter
from backend.app.schemas.generation import GenerationInput, GenerationResult

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a facts-only Mutual Fund FAQ Assistant for HDFC Mutual Fund schemes.
You provide objective, verifiable information sourced exclusively from the provided context.

STRICT OPERATIONAL RULES:
1. Provide factual information ONLY. Do NOT give investment advice, opinions, or recommendations.
2. Answer in NO MORE THAN 3 SENTENCES.
3. Rely strictly on the facts present in the provided context. Do NOT extrapolate or speculate.
4. If the question cannot be answered purely from the provided context, state that clearly."""


class GroundedGenerator:
    """Grounded LLM synthesizer with zero-temperature inference and deterministic fallback."""

    def __init__(
        self,
        validator: Optional[OutputValidator] = None,
        groq_client: Optional[AsyncGroq] = None,
        rate_limiter: Optional[GroqRateLimiter] = None,
    ) -> None:
        self.settings = get_settings()
        self.validator = validator or OutputValidator()
        self.client = groq_client or (AsyncGroq(api_key=self.settings.groq_api_key) if self.settings.groq_api_key else None)
        self.model_name = self.settings.groq_model or "openai/gpt-oss-120b"
        self.rate_limiter = rate_limiter or GroqRateLimiter(
            rpm_limit=self.settings.groq_rpm_limit,
            rpd_limit=self.settings.groq_rpd_limit,
            tpm_limit=self.settings.groq_tpm_limit,
            tpd_limit=self.settings.groq_tpd_limit,
        )

    async def _call_groq(self, prompt: str, system_prompt: str = SYSTEM_PROMPT) -> tuple[str, int]:
        """Call Groq API asynchronously using openai/gpt-oss-120b at temperature 0.0."""
        if not self.client or not self.settings.groq_api_key:
            raise ValueError("Groq API key not configured. Activating deterministic fallback.")

        response = await self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt},
            ],
            temperature=self.settings.groq_temperature,
            max_tokens=self.settings.groq_max_tokens,
        )

        content = ""
        total_tokens = self.settings.groq_max_tokens + 50
        if response.choices and len(response.choices) > 0:
            content = response.choices[0].message.content or ""
        
        if hasattr(response, "usage") and response.usage:
            total_tokens = getattr(response.usage, "total_tokens", total_tokens)

        return content, total_tokens

    def _fallback_synthesis(self, input_data: GenerationInput) -> str:
        """Deterministic fallback engine generating verified factual response directly from chunk."""
        return input_data.chunk_content

    async def generate(self, input_data: GenerationInput) -> GenerationResult:
        """Generate a constrained factual answer from retrieved chunk with output validation.
        
        Args:
            input_data: GenerationInput containing query, chunk_content, and canonical metadata.

        Returns:
            Validated GenerationResult strictly adhering to format constraints.
        """
        start_time = time.perf_counter()
        raw_output: Optional[str] = None
        is_fallback = False

        user_prompt = (
            f"Context Information:\n"
            f"---\n"
            f"{input_data.chunk_content}\n"
            f"---\n\n"
            f"User Question: {input_data.query}\n\n"
            f"Provide a concise factual answer in at most 3 sentences based only on the context above."
        )

        # 1. Proactive Rate & Token Budget Check (30 RPM, 8K TPM, 1K RPD, 200K TPD)
        estimated_tokens = len(user_prompt.split()) + self.settings.groq_max_tokens + 80
        can_call_groq, quota_reason = self.rate_limiter.can_proceed(estimated_tokens=estimated_tokens)

        if not can_call_groq:
            logger.warning("Groq rate limit threshold reached (%s). Gracefully falling back to deterministic synthesis.", quota_reason)
            raw_output = self._fallback_synthesis(input_data)
            is_fallback = True
        elif self.client and self.settings.groq_api_key:
            try:
                raw_output, tokens_used = await self._call_groq(prompt=user_prompt)
                self.rate_limiter.record_usage(tokens_used=tokens_used)
            except RateLimitError as rle:
                logger.warning("Groq HTTP 429 RateLimitError received (%s). Activating deterministic fallback.", rle)
                raw_output = self._fallback_synthesis(input_data)
                is_fallback = True
            except Exception as e:
                logger.warning("Groq inference encountered an error (%s). Activating deterministic fallback.", e)
                raw_output = self._fallback_synthesis(input_data)
                is_fallback = True
        else:
            raw_output = self._fallback_synthesis(input_data)
            is_fallback = True

        # 2. Programmatic Output Validation & Conformance Enforcement
        validated_text, sentence_count = self.validator.validate_and_format(
            raw_text=raw_output,
            canonical_url=input_data.canonical_url,
            last_updated=input_data.last_updated,
            max_sentences=self.settings.max_sentence_limit,
            requires_disclaimer=input_data.requires_disclaimer,
            disclaimer_text=self.settings.default_disclaimer,
        )

        latency = (time.perf_counter() - start_time) * 1000.0

        return GenerationResult(
            response=validated_text,
            raw_llm_output=raw_output,
            model=self.model_name if not is_fallback else "deterministic-fallback",
            sentence_count=sentence_count,
            source_url=input_data.canonical_url,
            last_updated=input_data.last_updated,
            disclaimer=self.settings.default_disclaimer,
            is_fallback=is_fallback,
            latency_ms=round(latency, 2),
        )
