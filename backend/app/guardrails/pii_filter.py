"""PII Detector and Scrubber for Indian Financial & Personal Data.

Enforces zero data ingestion by detecting and blocking standard and obfuscated
PAN, Aadhaar, phone numbers, emails, OTPs, and bank account numbers.
"""

import re
from typing import List, Tuple

from backend.app.schemas.guardrails import PIICheckResult, PIIType


class PIIFilter:
    """Multi-pattern regex detector and sanitizer defending against plain and obfuscated PII."""

    # Standard Regex Patterns
    PAN_PATTERN = re.compile(r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", re.IGNORECASE)
    AADHAAR_PATTERN = re.compile(r"\b[2-9]\d{3}[\s-]?[0-9]{4}[\s-]?[0-9]{4}\b")
    PHONE_PATTERN = re.compile(r"\b(?:\+91[\s-]?)?[6-9]\d{9}\b")
    EMAIL_PATTERN = re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b")
    OTP_PATTERN = re.compile(
        r"\b(?:otp|one[\s-]time[\s-]password|verification[\s-]code|security[\s-]code|auth[\s-]code|pin)\b[^\d\n]{0,25}\b([0-9]{4,8})\b",
        re.IGNORECASE,
    )
    ACCOUNT_PATTERN = re.compile(r"\b(?:a/c|account|folio|acc)[\s#:]*([0-9]{8,18})\b", re.IGNORECASE)

    # Obfuscated / Compressed Patterns (spaces/hyphens removed)
    COMPRESSED_PAN_PATTERN = re.compile(r"[A-Z]{5}[0-9]{4}[A-Z]")
    COMPRESSED_AADHAAR_PATTERN = re.compile(r"[2-9][0-9]{11}")
    COMPRESSED_PHONE_PATTERN = re.compile(r"(?:91)?[6-9][0-9]{9}")

    SECURITY_ALERT_MESSAGE = (
        "Security Notice: Your query contains sensitive personal or financial identification details "
        "(e.g., PAN, Aadhaar, phone, OTP, or account information). To protect your privacy and security, "
        "personal data is blocked and will not be processed or stored. Please submit queries without personal credentials."
    )

    def _detect_pan(self, raw_query: str) -> Tuple[bool, str]:
        """Detect standard and spaced/obfuscated PAN numbers (e.g. 'A B C D E 1 2 3 4 F')."""
        # 1. Direct standard check
        if self.PAN_PATTERN.search(raw_query):
            sanitized = self.PAN_PATTERN.sub("[REDACTED_PAN]", raw_query)
            return True, sanitized

        # 2. Obfuscation check: strip whitespaces and punctuation
        compressed = re.sub(r"[\s\-_.]", "", raw_query.upper())
        match = self.COMPRESSED_PAN_PATTERN.search(compressed)
        if match:
            # Mask detected characters from original query
            return True, "[REDACTED_OBFUSCATED_PAN]"

        return False, raw_query

    def _detect_aadhaar(self, raw_query: str) -> Tuple[bool, str]:
        """Detect standard and spaced Aadhaar numbers (12 digits starting 2-9)."""
        if self.AADHAAR_PATTERN.search(raw_query):
            sanitized = self.AADHAAR_PATTERN.sub("[REDACTED_AADHAAR]", raw_query)
            return True, sanitized

        # Compressed 12-digit sequence check
        digits_only = re.sub(r"[\s\-_.]", "", raw_query)
        if self.COMPRESSED_AADHAAR_PATTERN.search(digits_only) and ("aadhaar" in raw_query.lower() or "uid" in raw_query.lower()):
            return True, "[REDACTED_AADHAAR]"

        return False, raw_query

    def _detect_phone(self, raw_query: str) -> Tuple[bool, str]:
        """Detect 10-digit Indian mobile numbers (starting with 6,7,8,9)."""
        if self.PHONE_PATTERN.search(raw_query):
            sanitized = self.PHONE_PATTERN.sub("[REDACTED_PHONE]", raw_query)
            return True, sanitized

        # Obfuscated spaced 10 digits
        digits_only = re.sub(r"[\s\-_.]", "", raw_query)
        if self.COMPRESSED_PHONE_PATTERN.search(digits_only) and ("call" in raw_query.lower() or "phone" in raw_query.lower() or "mobile" in raw_query.lower() or "contact" in raw_query.lower() or "number" in raw_query.lower()):
            return True, "[REDACTED_PHONE]"

        return False, raw_query

    def _detect_email(self, raw_query: str) -> Tuple[bool, str]:
        """Detect email addresses."""
        if self.EMAIL_PATTERN.search(raw_query):
            sanitized = self.EMAIL_PATTERN.sub("[REDACTED_EMAIL]", raw_query)
            return True, sanitized
        return False, raw_query

    def _detect_otp(self, raw_query: str) -> Tuple[bool, str]:
        """Detect OTP and verification PIN codes."""
        if self.OTP_PATTERN.search(raw_query):
            sanitized = self.OTP_PATTERN.sub(r"\1 [REDACTED_OTP]", raw_query)
            return True, sanitized
        return False, raw_query

    def _detect_account(self, raw_query: str) -> Tuple[bool, str]:
        """Detect bank account or folio numbers."""
        if self.ACCOUNT_PATTERN.search(raw_query):
            sanitized = self.ACCOUNT_PATTERN.sub(r"[REDACTED_ACCOUNT]", raw_query)
            return True, sanitized
        return False, raw_query

    def check(self, query: str) -> PIICheckResult:
        """Scan query for all PII patterns and return structured result.
        
        Args:
            query: Raw user query string.

        Returns:
            PIICheckResult with is_pii_detected boolean and sanitized query.
        """
        detected_types: List[PIIType] = []
        current_text = query

        # 1. PAN Check
        has_pan, current_text = self._detect_pan(current_text)
        if has_pan:
            detected_types.append(PIIType.PAN)

        # 2. Aadhaar Check
        has_aadhaar, current_text = self._detect_aadhaar(current_text)
        if has_aadhaar:
            detected_types.append(PIIType.AADHAAR)

        # 3. Phone Check
        has_phone, current_text = self._detect_phone(current_text)
        if has_phone:
            detected_types.append(PIIType.PHONE)

        # 4. Email Check
        has_email, current_text = self._detect_email(current_text)
        if has_email:
            detected_types.append(PIIType.EMAIL)

        # 5. OTP Check
        has_otp, current_text = self._detect_otp(current_text)
        if has_otp:
            detected_types.append(PIIType.OTP)

        # 6. Account / Folio Check
        has_account, current_text = self._detect_account(current_text)
        if has_account:
            detected_types.append(PIIType.BANK_ACCOUNT)

        is_detected = len(detected_types) > 0

        return PIICheckResult(
            is_pii_detected=is_detected,
            detected_types=detected_types,
            masked_query=current_text if is_detected else query,
            security_message=self.SECURITY_ALERT_MESSAGE if is_detected else None,
        )
