"""Intent Classifier and Policy Router for Mutual Fund Compliance.

Classifies incoming user queries into FACTUAL, ADVISORY, COMPARISON,
PERFORMANCE_CALC, LIVE_NAV_PRICE, PROMPT_INJECTION, or MIXED_INTENT.
"""

import re
from typing import List, Optional, Tuple

from backend.app.schemas.guardrails import IntentClassificationResult, QueryIntent


class IntentRouter:
    """Compliance policy router detecting prohibited advisory, calculation, or adversarial queries."""

    # Prohibited Advisory & Suitability Patterns
    ADVISORY_PATTERNS = [
        r"\b(?:should\s+i\s+(?:invest|buy|put\s+money|start|choose|pick))\b",
        r"\b(?:is\s+.*?\s+(?:a\s+)?(?:good|best|safe|profitable|recommended)\s+(?:for|to|in|fund|choice|investment|option))\b",
        r"\b(?:which\s+(?:fund|scheme)\s+is\s+(?:the\s+)?(?:best|better|safest|top|recommended|good))\b",
        r"\b(?:recommend\s+(?:me\s+)?(?:a\s+)?(?:fund|scheme|investment|stock|mutual\s+fund))\b",
        r"\b(?:give\s+(?:me\s+)?(?:financial\s+)?advice|financial\s+planning\s+advice|suggest\s+(?:a\s+)?fund)\b",
        r"\b(?:suitable\s+for|is\s+.*?\s+suitable)\b",
        r"\b(?:good\s+for\s+.*?(?:portfolio|retirement|beginners?|retirees?|seniors?))\b",
        r"\b(?:for\s+my\s+age|my\s+portfolio|risk\s+appetite)\b",
        r"\b(?:i\s+am\s+\d+\s+years?\s+old|for\s+a\s+beginner|good\s+for\s+retirees?)\b",
        r"\b(?:will\s+i\s+(?:make|lose)\s+money|will\s+it\s+(?:double|grow|go\s+up|crash))\b",
        r"\b(?:will\s+.*?\s+(?:go\s+up|go\s+down|increase|double|grow|crash|perform))\b",
        r"\b(?:future\s+price|price\s+prediction|target\s+price|predict\s+(?:the\s+)?price)\b",
    ]

    # Comparative Ranking & Advice Patterns
    COMPARISON_PATTERNS = [
        r"\b(?:which\s+is\s+better|which\s+one\s+is\s+better|which\s+is\s+best)\b",
        r"\b(?:compare\s+.*\s+(?:and|with|vs)\s+.*(?:which|better|more\s+return))\b",
        r"\b(?:which\s+(?:gives|offers|has)\s+(?:higher|more|better)\s+returns?)\b",
        r"\b(?:is\s+.*\s+better\s+than\s+.*)\b",
    ]

    # Hypothetical Return / Compound Interest Projections Patterns
    PERFORMANCE_CALC_PATTERNS = [
        r"\b(?:calculate\s+(?:my\s+)?(?:returns?|profit|cagr|maturity|growth))\b",
        r"\b(?:how\s+much\s+(?:will|can)\s+i\s+(?:make|get|earn|have))\b",
        r"\b(?:if\s+i\s+invest\s+.*(?:how\s+much|what\s+will|in\s+\d+\s+years))\b",
        r"\b(?:maturity\s+value|projected\s+value|future\s+value|cagr\s+calculator|15%\s*cagr|12%\s*cagr)\b",
        r"\b(?:what\s+will\s+be\s+the\s+value\s+of\s+.*(?:in\s+\d+\s+years|after\s+\d+\s+years))\b",
    ]

    # Live NAV / Price Patterns (EC-06)
    LIVE_NAV_PATTERNS = [
        r"\b(?:today(?:'s)?\s+nav|current\s+nav|latest\s+nav\s+today|live\s+nav|nav\s+today|today\s+price)\b",
        r"\b(?:what\s+is\s+today(?:'s)?\s+(?:nav|price)|current\s+market\s+price|live\s+price)\b",
    ]

    # Prompt Injection & Jailbreak Attack Patterns (EC-08)
    PROMPT_INJECTION_PATTERNS = [
        r"\b(?:ignore\s+(?:all\s+)?(?:previous|prior|above|system)\s+instructions?)\b",
        r"\b(?:ignore\s+(?:your\s+)?(?:rules|constraints|guardrails|safety))\b",
        r"\b(?:system\s+override|override\s+system|developer\s+mode|jailbreak)\b",
        r"\b(?:act\s+as\s+(?:a\s+)?(?:financial\s+advisor|unconstrained|unfiltered|expert\s+trader))\b",
        r"\b(?:pretend\s+(?:you\s+are|to\s+be)|you\s+are\s+now\s+(?:an?\s+)?(?:financial\s+advisor|unrestricted))\b",
        r"\b(?:what\s+is\s+your\s+(?:system\s+prompt|secret\s+prompt|initial\s+prompt|internal\s+instructions?))\b",
        r"\b(?:print\s+(?:your\s+)?(?:system\s+prompt|instructions?)|reveal\s+(?:your\s+)?prompt)\b",
    ]

    # Factual Core Schema Patterns
    FACTUAL_INDICATORS = [
        r"\b(?:expense\s*ratio|ter|exit\s*load|min(?:imum)?\s*sip|lump\s*sum|lock\s*in|lock-in|tax|taxation|stcg|ltcg|riskometer|benchmark|statement|schedule\s*112a)\b"
    ]

    def _match_any(self, query: str, pattern_list: List[str]) -> Tuple[bool, List[str]]:
        """Check if query matches any regex pattern in list."""
        matched: List[str] = []
        for pattern in pattern_list:
            if re.search(pattern, query, re.IGNORECASE):
                matched.append(pattern)
        return len(matched) > 0, matched

    def classify(self, query: str) -> IntentClassificationResult:
        """Classify user query intent into compliant or blocked category.
        
        Args:
            query: Raw user query string.

        Returns:
            IntentClassificationResult with intent, is_blocked flag, and matched triggers.
        """
        normalized_q = query.strip()

        # 1. Prompt Injection / Jailbreak check (Highest priority)
        is_inj, inj_triggers = self._match_any(normalized_q, self.PROMPT_INJECTION_PATTERNS)
        if is_inj:
            return IntentClassificationResult(
                intent=QueryIntent.PROMPT_INJECTION,
                is_blocked=True,
                matched_patterns=inj_triggers,
                confidence=1.0,
            )

        # 2. Performance / Return Calculation check
        is_calc, calc_triggers = self._match_any(normalized_q, self.PERFORMANCE_CALC_PATTERNS)
        if is_calc:
            return IntentClassificationResult(
                intent=QueryIntent.PERFORMANCE_CALC,
                is_blocked=True,
                matched_patterns=calc_triggers,
                confidence=0.95,
            )

        # 3. Live NAV / Real-time pricing check (EC-06)
        is_nav, nav_triggers = self._match_any(normalized_q, self.LIVE_NAV_PATTERNS)
        if is_nav:
            return IntentClassificationResult(
                intent=QueryIntent.LIVE_NAV_PRICE,
                is_blocked=True,
                matched_patterns=nav_triggers,
                confidence=0.95,
            )

        # 4. Comparative advice check (EC-03)
        is_comp, comp_triggers = self._match_any(normalized_q, self.COMPARISON_PATTERNS)
        if is_comp:
            return IntentClassificationResult(
                intent=QueryIntent.COMPARISON,
                is_blocked=True,
                matched_patterns=comp_triggers,
                confidence=0.90,
            )

        # 5. Direct Advisory check
        is_adv, adv_triggers = self._match_any(normalized_q, self.ADVISORY_PATTERNS)

        # 6. Check for Mixed Intent (EC-04: Fact + Advice)
        is_fact, _ = self._match_any(normalized_q, self.FACTUAL_INDICATORS)
        if is_adv and is_fact:
            # Extract factual subquery if possible
            # e.g., "What is the lock-in for ELSS and should I invest now?"
            factual_part = re.sub(r"(?:and|,|\?)\s*(?:should\s+i|is\s+it\s+good|recommend).*", "", normalized_q, flags=re.IGNORECASE).strip()
            return IntentClassificationResult(
                intent=QueryIntent.MIXED_INTENT,
                is_blocked=False,  # Allow factual pipeline to answer factual part
                matched_patterns=adv_triggers,
                confidence=0.85,
                factual_subquery=factual_part if factual_part else normalized_q,
                requires_disclaimer=True,
            )

        if is_adv:
            return IntentClassificationResult(
                intent=QueryIntent.ADVISORY,
                is_blocked=True,
                matched_patterns=adv_triggers,
                confidence=0.95,
            )

        # 7. Default: Factual Scheme / Operations Query
        return IntentClassificationResult(
            intent=QueryIntent.FACTUAL,
            is_blocked=False,
            matched_patterns=[],
            confidence=1.0,
        )
