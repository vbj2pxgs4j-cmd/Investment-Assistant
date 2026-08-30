"""Programmatic Output Validator and Conformance Enforcement Engine.

Enforces strict compliance on LLM generation:
1. Hard upper bound of <= 3 sentences using financial abbreviation-aware tokenizer.
2. Single canonical Groww citation URL (stripping hallucinated/duplicate links).
3. Standardized timestamp footer ('Last updated from sources: YYYY-MM-DD').
"""

import re
from typing import List, Optional, Tuple

from backend.app.core.config import get_settings


class OutputValidator:
    """Deterministic validator enforcing sentence limits, citation integrity, and footers."""

    def __init__(self) -> None:
        self.settings = get_settings()

    @staticmethod
    def split_into_sentences(text: str) -> List[str]:
        """Split text into semantic sentences while protecting financial abbreviations and numbers.
        
        Protects: Rs., min., max., approx., e.g., i.e., vs., reg., mo., TER., No., decimal numbers, etc.
        """
        # List of abbreviations to protect (case-insensitive)
        abbreviations = [
            "Rs", "min", "max", "approx", "vs", "reg", "mo", "no", "vol", "ter",
            "e.g", "i.e", "dr", "mr", "mrs", "ms", "prof", "sr", "jr", "co", "corp", "inc", "ltd"
        ]
        temp_text = text.strip()

        # Protect abbreviations followed by period
        for abbrev in abbreviations:
            pattern = re.compile(rf"\b({re.escape(abbrev)})\.", re.IGNORECASE)
            temp_text = pattern.sub(r"\1__DOT__", temp_text)

        # Protect numbers with decimal points (e.g., 0.74%, 1.65%)
        temp_text = re.sub(r"(\d+)\.(\d+)", r"\1__DECIMAL__\2", temp_text)

        # Split on sentence boundaries: period, question mark, exclamation followed by whitespace and uppercase/numeral/quote
        split_pattern = r"(?<=[.!?])\s+(?=[A-Z0-9₹\"'\(\[])"
        raw_splits = re.split(split_pattern, temp_text)

        sentences = []
        for s in raw_splits:
            restored = s.replace("__DOT__", ".").replace("__DECIMAL__", ".").strip()
            if restored:
                sentences.append(restored)
        return sentences

    @staticmethod
    def strip_unwanted_artifacts(text: str) -> str:
        """Strip raw links, markdown citations, markdown headers, and timestamp lines from body text."""
        # 1. Strip markdown links [label](url) -> label
        clean = re.sub(r"\[([^\]]+)\]\((https?://[^\)]+)\)", r"\1", text)

        # 2. Strip raw URLs
        clean = re.sub(r"https?://\S+|www\.\S+", "", clean)

        # 3. Strip stray citation tags like [1], [Source], (Source: ...), etc.
        clean = re.sub(r"\[\s*\d+\s*\]", "", clean)
        clean = re.sub(r"\[\s*Source:?[^\]]*\]", "", clean, flags=re.IGNORECASE)
        clean = re.sub(r"\(\s*Source:?[^\)]*\)", "", clean, flags=re.IGNORECASE)
        clean = re.sub(r"(?i)Source\s*:\s*", "", clean)

        # 4. Strip existing timestamp footer lines if present in raw text
        clean = re.sub(r"(?i)Last\s+updated\s+from\s+sources?\s*:\s*\d{4}-\d{2}-\d{2}", "", clean)

        # 5. Strip markdown headers or bullet points
        clean = re.sub(r"^#+\s*", "", clean, flags=re.MULTILINE)
        clean = re.sub(r"^[\*\-]\s*", "", clean, flags=re.MULTILINE)

        # 6. Normalize whitespace
        clean = re.sub(r"[ \t]+", " ", clean)
        clean = re.sub(r"\n\s*\n+", " ", clean).strip()

        return clean

    def validate_and_format(
        self,
        raw_text: str,
        canonical_url: str,
        last_updated: str = "2024-04-01",
        max_sentences: int = 3,
        requires_disclaimer: bool = False,
        disclaimer_text: Optional[str] = None,
    ) -> Tuple[str, int]:
        """Validate, truncate, and format raw generation into compliant response.
        
        Args:
            raw_text: Raw output string from LLM or fallback synthesis.
            canonical_url: Single authoritative whitelisted Groww URL.
            last_updated: Canonical source date in YYYY-MM-DD format.
            max_sentences: Maximum allowed sentences in factual answer (default 3).
            requires_disclaimer: True if additional non-advisory disclaimer is needed.
            disclaimer_text: Custom disclaimer string if required.

        Returns:
            Tuple of (formatted_final_string, calculated_sentence_count).
        """
        # Step 1: Strip unwanted URLs, tags, and footers from body
        cleaned_body = self.strip_unwanted_artifacts(raw_text)

        # Step 2: Tokenize and enforce max sentence limit
        sentences = self.split_into_sentences(cleaned_body)
        if len(sentences) > max_sentences:
            sentences = sentences[:max_sentences]

        # Step 3: Reassemble sentences into clean paragraph
        body_paragraph = " ".join(sentences).strip()

        # Step 4: Ensure concluding punctuation
        if body_paragraph and not body_paragraph[-1] in ".!?":
            body_paragraph += "."

        # Step 5: Enforce canonical URL validation (must be under groww.in)
        validated_url = canonical_url if "groww.in" in canonical_url else "https://groww.in/mutual-funds"

        # Step 6: Assemble final formatted payload
        final_parts = [
            body_paragraph,
            f"Source: {validated_url}",
            f"Last updated from sources: {last_updated}",
        ]

        if requires_disclaimer:
            disc = disclaimer_text or self.settings.default_disclaimer
            final_parts.append(f"Disclaimer: {disc}")

        final_response = "\n\n".join(final_parts[:1]) + "\n\n" + "\n".join(final_parts[1:])
        sentence_count = len(sentences)

        return final_response, sentence_count
