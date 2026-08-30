"""Unit and integration tests for GroundedGenerator, GroqRateLimiter, and synthesis formatting."""

import os
import pytest
from unittest.mock import AsyncMock, MagicMock

from groq import AsyncGroq, RateLimitError

from backend.app.core.config import get_settings
from backend.app.rag.generator import GroundedGenerator
from backend.app.rag.rate_limiter import GroqRateLimiter
from backend.app.schemas.generation import GenerationInput


@pytest.fixture
def generator() -> GroundedGenerator:
    # Generator without Groq key operates in deterministic fallback mode
    return GroundedGenerator()


@pytest.mark.asyncio
async def test_fallback_generation_across_schemes(generator: GroundedGenerator):
    """Verify that deterministic fallback generates valid conforming responses across schemes."""
    test_cases = [
        (
            "What is the exit load of HDFC Mid-Cap Fund?",
            "For units redeemed or switched out within 1 year (365 days) from the date of allotment, an exit load of 1.00% is applicable. No exit load is payable for units redeemed after 1 year.",
            "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
        ),
        (
            "What is the lock-in period for HDFC ELSS?",
            "Statutory lock-in period of 3 years (36 months) applies to every installment. Units cannot be redeemed, transferred, or pledged before the completion of 3 years.",
            "https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth",
        ),
        (
            "What is the TER of HDFC Top 100 Fund?",
            "The Total Expense Ratio (TER) for Direct Plan - Growth is 1.08% inclusive of GST. Regular Plan TER is 1.68%.",
            "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth",
        ),
    ]

    for query, content, url in test_cases:
        inp = GenerationInput(
            query=query,
            chunk_content=content,
            canonical_url=url,
            last_updated="2024-04-01",
        )
        res = await generator.generate(inp)
        assert res.sentence_count <= 3
        assert res.sentence_count >= 1
        assert res.source_url == url
        assert "Last updated from sources: 2024-04-01" in res.response
        assert res.is_fallback is True


@pytest.mark.asyncio
async def test_mocked_groq_generation():
    """Verify that Groq model generation with openai/gpt-oss-120b passes validation."""
    mock_choice = MagicMock()
    mock_choice.message.content = (
        "The minimum SIP amount for HDFC Small Cap Fund is ₹100 per month. "
        "Investors can also invest a minimum lump sum amount of ₹100. "
        "Check Groww for more details."
    )
    mock_response = MagicMock()
    mock_response.choices = [mock_choice]
    mock_response.usage.total_tokens = 120

    mock_groq_client = MagicMock()
    mock_groq_client.chat.completions.create = AsyncMock(return_value=mock_response)

    gen = GroundedGenerator(groq_client=mock_groq_client)
    gen.settings.groq_api_key = "test_key_mock"

    inp = GenerationInput(
        query="What is the minimum SIP for HDFC Small Cap?",
        chunk_content="Minimum SIP is ₹100 and minimum lump sum is ₹100.",
        canonical_url="https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
        last_updated="2024-04-01",
    )

    res = await gen.generate(inp)
    assert res.model == "openai/gpt-oss-120b"
    assert res.is_fallback is False
    assert res.sentence_count <= 3
    assert "https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth" in res.response
    assert "Last updated from sources: 2024-04-01" in res.response


@pytest.mark.asyncio
async def test_generator_recovers_from_groq_exception():
    """Verify that generator gracefully switches to fallback on Groq API exception."""
    mock_groq_client = MagicMock()
    mock_groq_client.chat.completions.create = AsyncMock(side_effect=Exception("Groq API Timeout"))

    gen = GroundedGenerator(groq_client=mock_groq_client)
    gen.settings.groq_api_key = "test_key_mock"

    inp = GenerationInput(
        query="What is the exit load for HDFC Gold FoF?",
        chunk_content="Exit load is 1.00% if redeemed within 15 days of allotment.",
        canonical_url="https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth",
        last_updated="2024-04-01",
    )

    res = await gen.generate(inp)
    assert res.is_fallback is True
    assert res.sentence_count <= 3
    assert "15 days" in res.response
    assert "https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth" in res.response


def test_rate_limiter_rpm_enforcement():
    """Verify that GroqRateLimiter strictly enforces the 30 RPM limit."""
    limiter = GroqRateLimiter(rpm_limit=30, rpd_limit=1000, tpm_limit=8000, tpd_limit=200000)

    for _ in range(30):
        allowed, reason = limiter.can_proceed(estimated_tokens=50)
        assert allowed is True
        limiter.record_usage(tokens_used=50)

    # 31st request should be blocked
    allowed, reason = limiter.can_proceed(estimated_tokens=50)
    assert allowed is False
    assert "RPM limit reached" in reason


def test_rate_limiter_tpm_enforcement():
    """Verify that GroqRateLimiter enforces the 8,000 TPM limit."""
    limiter = GroqRateLimiter(rpm_limit=30, rpd_limit=1000, tpm_limit=8000, tpd_limit=200000)

    # Record 7,900 tokens
    limiter.record_usage(tokens_used=7900)

    # Request requiring 200 tokens should be rejected (7900 + 200 > 8000)
    allowed, reason = limiter.can_proceed(estimated_tokens=200)
    assert allowed is False
    assert "TPM limit exceeded" in reason


def test_rate_limiter_daily_limits():
    """Verify that RPD (1000) and TPD (200000) daily quotas are enforced."""
    limiter = GroqRateLimiter(rpm_limit=100, rpd_limit=5, tpm_limit=50000, tpd_limit=1000)

    for _ in range(5):
        limiter.record_usage(tokens_used=50)

    allowed, reason = limiter.can_proceed(estimated_tokens=50)
    assert allowed is False
    assert "RPD limit reached" in reason


@pytest.mark.asyncio
async def test_generator_proactive_rate_limit_fallback():
    """Verify that when RPM/TPM quota is exhausted, generator proactively executes fallback without calling Groq."""
    limiter = GroqRateLimiter(rpm_limit=1, rpd_limit=1000, tpm_limit=8000, tpd_limit=200000)
    limiter.record_usage(tokens_used=100)  # Exhaust 1 RPM budget

    mock_groq_client = MagicMock()
    mock_groq_client.chat.completions.create = AsyncMock()

    gen = GroundedGenerator(groq_client=mock_groq_client, rate_limiter=limiter)
    gen.settings.groq_api_key = "test_key"

    inp = GenerationInput(
        query="What is the lock-in period for HDFC ELSS?",
        chunk_content="Statutory lock-in period of 3 years applies.",
        canonical_url="https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth",
        last_updated="2024-04-01",
    )

    res = await gen.generate(inp)
    assert res.is_fallback is True
    assert "3 years" in res.response
    # External API should never have been called
    mock_groq_client.chat.completions.create.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.skipif(
    not os.environ.get("GROQ_API_KEY") or os.environ.get("GROQ_API_KEY") == "your_groq_api_key_here",
    reason="Live Groq API Key not set in environment",
)
async def test_live_groq_generation_integration():
    """Live integration test executing an actual Groq inference with openai/gpt-oss-120b."""
    api_key = os.environ.get("GROQ_API_KEY")
    live_client = AsyncGroq(api_key=api_key)

    generator = GroundedGenerator(groq_client=live_client)
    generator.settings.groq_api_key = api_key

    inp = GenerationInput(
        query="What is the exit load for HDFC Small Cap Fund?",
        chunk_content=(
            "For units redeemed or switched out within 1 year (365 days) from the date of allotment, "
            "an exit load of 1.00% is applicable. No exit load is payable for units redeemed after 1 year."
        ),
        canonical_url="https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
        last_updated="2024-04-01",
    )

    res = await generator.generate(inp)
    assert res.sentence_count <= 3
    assert res.sentence_count >= 1
    assert "https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth" in res.response
    assert "Last updated from sources: 2024-04-01" in res.response
    assert res.is_fallback is False
    assert res.model == "openai/gpt-oss-120b"
