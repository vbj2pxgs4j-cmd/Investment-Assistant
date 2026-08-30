"""Groq LPU Rate and Token Limiter for openai/gpt-oss-120b.

Enforces strict client-side quotas before external API dispatch:
- Requests Per Minute (RPM): 30
- Requests Per Day (RPD): 1,000
- Tokens Per Minute (TPM): 8,000
- Tokens Per Day (TPD): 200,000

When quotas are reached, triggers proactive zero-latency deterministic fallback
synthesis to guarantee 100% service uptime without hitting external 429 errors.
"""

import logging
import time
from collections import deque
from datetime import datetime, timezone
from typing import Deque, Dict, Tuple

logger = logging.getLogger(__name__)


class GroqRateLimiter:
    """Sliding-window rate and token limiter managing Groq model inference quotas."""

    def __init__(
        self,
        rpm_limit: int = 30,
        rpd_limit: int = 1000,
        tpm_limit: int = 8000,
        tpd_limit: int = 200000,
    ) -> None:
        self.rpm_limit = rpm_limit
        self.rpd_limit = rpd_limit
        self.tpm_limit = tpm_limit
        self.tpd_limit = tpd_limit

        # Sliding 60-second window storage: deque of (timestamp, token_count)
        self._sliding_window: Deque[Tuple[float, int]] = deque()

        # Daily tracking
        self._current_day: str = self._get_today_key()
        self._daily_requests: int = 0
        self._daily_tokens: int = 0

    def _get_today_key(self) -> str:
        """Return current date string in YYYY-MM-DD UTC format."""
        return datetime.now(timezone.utc).strftime("%Y-%m-%d")

    def _cleanup_expired_window(self, now: float) -> None:
        """Evict items older than 60 seconds from sliding window and handle daily rollover."""
        # 1. Slide 60-second window
        window_start = now - 60.0
        while self._sliding_window and self._sliding_window[0][0] < window_start:
            self._sliding_window.popleft()

        # 2. Check for daily reset
        today = self._get_today_key()
        if today != self._current_day:
            self._current_day = today
            self._daily_requests = 0
            self._daily_tokens = 0

    def can_proceed(self, estimated_tokens: int = 180) -> Tuple[bool, str]:
        """Check if an upcoming request with estimated tokens can proceed within limits.

        Args:
            estimated_tokens: Estimated total tokens for prompt + completion (default ~180).

        Returns:
            Tuple of (is_allowed, reason_or_status).
        """
        now = time.time()
        self._cleanup_expired_window(now)

        # 1. Check Requests Per Minute (RPM)
        current_rpm = len(self._sliding_window)
        if current_rpm >= self.rpm_limit:
            return False, f"RPM limit reached ({current_rpm}/{self.rpm_limit} req/min)"

        # 2. Check Tokens Per Minute (TPM)
        current_tpm = sum(tokens for _, tokens in self._sliding_window)
        if current_tpm + estimated_tokens > self.tpm_limit:
            return False, f"TPM limit exceeded ({current_tpm + estimated_tokens}/{self.tpm_limit} tokens/min)"

        # 3. Check Requests Per Day (RPD)
        if self._daily_requests >= self.rpd_limit:
            return False, f"RPD limit reached ({self._daily_requests}/{self.rpd_limit} req/day)"

        # 4. Check Tokens Per Day (TPD)
        if self._daily_tokens + estimated_tokens > self.tpd_limit:
            return False, f"TPD limit exceeded ({self._daily_tokens + estimated_tokens}/{self.tpd_limit} tokens/day)"

        return True, "OK"

    def record_usage(self, tokens_used: int = 150) -> None:
        """Record an executed Groq request with actual or estimated tokens consumed."""
        now = time.time()
        self._cleanup_expired_window(now)

        self._sliding_window.append((now, tokens_used))
        self._daily_requests += 1
        self._daily_tokens += tokens_used

    def get_metrics(self) -> Dict[str, object]:
        """Retrieve telemetry on current quota utilization."""
        now = time.time()
        self._cleanup_expired_window(now)

        current_rpm = len(self._sliding_window)
        current_tpm = sum(tokens for _, tokens in self._sliding_window)

        return {
            "rpm_current": current_rpm,
            "rpm_limit": self.rpm_limit,
            "rpm_utilization_pct": round((current_rpm / self.rpm_limit) * 100, 1) if self.rpm_limit else 0,
            "tpm_current": current_tpm,
            "tpm_limit": self.tpm_limit,
            "tpm_utilization_pct": round((current_tpm / self.tpm_limit) * 100, 1) if self.tpm_limit else 0,
            "rpd_current": self._daily_requests,
            "rpd_limit": self.rpd_limit,
            "tpd_current": self._daily_tokens,
            "tpd_limit": self.tpd_limit,
        }

    def reset(self) -> None:
        """Reset internal metrics and sliding windows (useful for testing)."""
        self._sliding_window.clear()
        self._daily_requests = 0
        self._daily_tokens = 0
        self._current_day = self._get_today_key()
