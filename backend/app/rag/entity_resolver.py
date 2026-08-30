"""Entity and Parameter Intent Resolver for Mutual Fund Queries.

Provides high-precision token/regex matching against scheme aliases,
domain parameters, general operations, ambiguity detection (EC-01),
and out-of-scope fund interception (EC-02).
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from backend.app.core.config import PROJECT_ROOT, get_settings
from backend.app.schemas.retrieval import (
    ParameterType,
    ResolutionStatus,
    ResolvedEntity,
)

# Canonical 5 Supported HDFC Schemes Metadata
SUPPORTED_SCHEMES_MAP = {
    "hdfc-mid-cap-fund-direct-growth": {
        "name": "HDFC Mid-Cap Opportunities Fund",
        "category": "Equity: Mid Cap",
        "canonical_url": "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
        "aliases": [
            "hdfc mid-cap opportunities fund",
            "hdfc mid cap opportunities fund",
            "hdfc mid-cap opportunities",
            "hdfc mid cap opportunities",
            "hdfc mid-cap fund",
            "hdfc mid cap fund",
            "hdfc mid-cap",
            "hdfc mid cap",
            "hdfc midcap",
            "mid-cap opportunities fund",
            "mid cap opportunities fund",
            "mid cap fund",
            "mid-cap fund",
            "mid cap",
            "midcap",
            "mid-cap",
        ],
    },
    "hdfc-small-cap-fund-direct-growth": {
        "name": "HDFC Small Cap Fund",
        "category": "Equity: Small Cap",
        "canonical_url": "https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
        "aliases": [
            "hdfc small cap fund",
            "hdfc small-cap fund",
            "hdfc small cap",
            "hdfc small-cap",
            "hdfc smallcap",
            "small cap fund",
            "small-cap fund",
            "small cap",
            "smallcap",
            "small-cap",
        ],
    },
    "hdfc-gold-etf-fund-of-fund-direct-plan-growth": {
        "name": "HDFC Gold ETF Fund of Fund",
        "category": "Commodities: Gold / Fund of Funds",
        "canonical_url": "https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth",
        "aliases": [
            "hdfc gold etf fund of fund",
            "hdfc gold etf fof",
            "hdfc gold etf fund",
            "hdfc gold etf",
            "hdfc gold fof",
            "hdfc gold fund of fund",
            "hdfc gold fund",
            "hdfc gold",
            "gold etf fund of fund",
            "gold etf fof",
            "gold etf fund",
            "gold fof",
            "gold etf",
            "gold fund",
        ],
    },
    "hdfc-large-cap-fund-direct-growth": {
        "name": "HDFC Top 100 / Large Cap Fund",
        "category": "Equity: Large Cap",
        "canonical_url": "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth",
        "aliases": [
            "hdfc top 100 / large cap fund",
            "hdfc top 100 fund",
            "hdfc top 100",
            "hdfc top100 fund",
            "hdfc top100",
            "hdfc large cap fund",
            "hdfc large-cap fund",
            "hdfc large cap",
            "hdfc large-cap",
            "hdfc largecap",
            "top 100 fund",
            "top 100",
            "top100",
            "large cap fund",
            "large-cap fund",
            "large cap",
            "largecap",
            "large-cap",
        ],
    },
    "hdfc-elss-tax-saver-fund-direct-plan-growth": {
        "name": "HDFC ELSS Tax Saver Fund",
        "category": "Equity: ELSS / Tax Saver",
        "canonical_url": "https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth",
        "aliases": [
            "hdfc elss tax saver fund",
            "hdfc elss tax saver",
            "hdfc elss fund",
            "hdfc elss",
            "hdfc tax saver fund",
            "hdfc tax saver",
            "hdfc tax sevar",
            "elss tax saver fund",
            "elss tax saver",
            "elss tax sevar",
            "tax saver fund",
            "tax saver",
            "tax sevar",
            "elss fund",
            "elss",
        ],
    },
}

# General Operations Keywords & Aliases
GENERAL_OPERATIONS_ALIASES = [
    "statement",
    "account statement",
    "statements",
    "capital gains",
    "capital gains report",
    "capital gains statement",
    "download statement",
    "download report",
    "tax statement",
    "itr statement",
    "itr report",
    "schedule 112a",
    "p&l statement",
    "p&l report",
    "folio",
    "educational resources",
    "amfi",
    "sebi portal",
]

# Out-of-Scope Competitor AMCs and Unsupported Funds (EC-02)
COMPETITOR_AMCS = [
    "sbi",
    "icici",
    "icici prudential",
    "axis",
    "nippon",
    "nippon india",
    "parag parikh",
    "ppfas",
    "mirae",
    "mirae asset",
    "kotak",
    "tata",
    "dsp",
    "quant",
    "uti",
    "motilal oswal",
    "canara robeco",
    "bandhan",
    "invesco",
    "franklin",
    "franklin templeton",
    "edelweiss",
    "hsbc",
    "sundaram",
    "baroda bnp",
    "pgim",
    "whiteoak",
    "zerodha",
    "groww mutual fund",
]

UNSUPPORTED_HDFC_SCHEMES = [
    "hdfc balanced advantage",
    "hdfc flexi cap",
    "hdfc hybrid",
    "hdfc defence",
    "hdfc manufacturing",
    "hdfc index",
    "hdfc dividend yield",
    "hdfc multi cap",
    "hdfc liquid fund",
    "hdfc overnight fund",
    "hdfc ultra short term",
]

# Parameter Domain Intent Heuristics
PARAMETER_PATTERNS: Dict[ParameterType, List[str]] = {
    ParameterType.EXPENSE_RATIO: [
        r"\b(?:ter|expense\s*ratio|expense\s*charges?|charges?|management\s*fee|annual\s*fee|cost\s*ratio|fees?)\b",
        r"\b(?:what\s+is\s+the\s+ter|how\s+much\s+is\s+the\s+expense)\b",
    ],
    ParameterType.EXIT_LOAD: [
        r"\b(?:exit\s*load|exit\s*penalty|redemption\s*charge|redemption\s*fee|redemption\s*penalty)\b",
        r"\b(?:holding\s*period|holding\s*duration|switch\s*out|exit\s*fee|early\s*redemption)\b",
        r"\b(?:365\s*days|15\s*days|1\s*year\s*exit)\b",
    ],
    ParameterType.INVESTMENT_LIMITS: [
        r"\b(?:min(?:imum)?\s*sip|sip\s*amount|sip\s*limit|sip\s*minimum|sip\s*instal[l]?ment)\b",
        r"\b(?:lump\s*sum|lumpsum|min(?:imum)?\s*lump\s*sum|min(?:imum)?\s*lumpsum)\b",
        r"\b(?:min(?:imum)?\s*investment|initial\s*investment|initial\s*purchase|additional\s*purchase|additional\s*investment)\b",
        r"\b(?:how\s+much\s+to\s+invest|start\s+sip)\b",
    ],
    ParameterType.LOCK_IN_PERIOD: [
        r"\b(?:lock\s*in|lock-in|lockin|lock\s*in\s*period|statutory\s*lock\s*in|mandatory\s*lock)\b",
        r"\b(?:3\s*years?\s*lock|when\s+can\s+i\s+withdraw|can\s+i\s+withdraw\s+anytime)\b",
    ],
    ParameterType.TAXATION: [
        r"\b(?:tax(?:ation)?|stcg|ltcg|section\s*80c|80c|capital\s*gains?\s*tax)\b",
        r"\b(?:short\s*term\s*capital\s*gains?|long\s*term\s*capital\s*gains?|tax\s*benefit|tax\s*exemption|tax\s*saving)\b",
        r"\b(?:12\.5%|20%|1\.25\s*lakh)\b",
    ],
    ParameterType.OPERATIONS: [
        r"\b(?:statement|download\s*statement|account\s*statement|capital\s*gains?\s*report)\b",
        r"\b(?:schedule\s*112a|p&l|itr\s*report|tax\s*statement|how\s+to\s+download|folio)\b",
    ],
    ParameterType.FUND_OVERVIEW: [
        r"\b(?:riskometer|risk\s*rating|risk\s*level|benchmark|benchmark\s*index|category|fund\s*category)\b",
        r"\b(?:amc|fund\s*manager|fund\s*objective|what\s+is\s+hdfc|about\s+hdfc|objective)\b",
    ],
}


class EntityResolver:
    """High-precision entity and parameter classifier for mutual fund queries."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.schemes_map = SUPPORTED_SCHEMES_MAP
        self.manifest_data = self._load_manifest()

    def _load_manifest(self) -> Dict[str, Any]:
        """Optionally load data/raw/sources_manifest.json for dynamic alias sync."""
        manifest_path = PROJECT_ROOT / "data" / "raw" / "sources_manifest.json"
        if manifest_path.exists():
            try:
                with open(manifest_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {}

    def normalize_query(self, query: str) -> str:
        """Normalize raw query: lowercasing, stripping extra whitespaces and punctuation."""
        q = query.lower().strip()
        # Replace non-alphanumeric chars (excluding hyphens and percentage) with single spaces
        q = re.sub(r"[^\w\s\-%₹.]", " ", q)
        q = re.sub(r"\s+", " ", q).strip()
        return q

    def detect_parameter(self, normalized_query: str) -> Tuple[ParameterType, Optional[str]]:
        """Identify target parameter domain from regex rules."""
        for param_type, patterns in PARAMETER_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, normalized_query, re.IGNORECASE):
                    return param_type, param_type.value
        return ParameterType.UNKNOWN, None

    def detect_out_of_scope(self, normalized_query: str) -> Optional[str]:
        """Detect mentions of competitor AMCs or unsupported HDFC funds (EC-02)."""
        # Check unsupported HDFC schemes first
        for unsupported in UNSUPPORTED_HDFC_SCHEMES:
            if unsupported in normalized_query:
                return unsupported.title()

        # Check competitor AMCs
        for amc in COMPETITOR_AMCS:
            # Match word boundary
            pattern = rf"\b{re.escape(amc)}\b"
            if re.search(pattern, normalized_query, re.IGNORECASE):
                # Ensure it's not simply an HDFC query containing incidental words
                if "hdfc" not in normalized_query or amc in ["sbi", "icici", "axis", "kotak", "tata", "dsp"]:
                    return amc.title()

        return None

    def match_scheme(self, normalized_query: str) -> Tuple[Optional[str], Optional[str], Optional[str], float]:
        """Match query against supported scheme aliases with longest-match priority.
        
        Returns:
            Tuple of (scheme_code, scheme_name, matched_alias, confidence)
        """
        best_match_code = None
        best_match_name = None
        best_alias = None
        longest_len = 0

        for scheme_code, scheme_info in self.schemes_map.items():
            for alias in scheme_info["aliases"]:
                # Ensure word-boundary or substring match
                pattern = rf"\b{re.escape(alias)}\b"
                match = re.search(pattern, normalized_query, re.IGNORECASE)
                if match:
                    alias_len = len(alias)
                    if alias_len > longest_len:
                        longest_len = alias_len
                        best_match_code = scheme_code
                        best_match_name = scheme_info["name"]
                        best_alias = alias

        if best_match_code:
            confidence = min(1.0, 0.7 + (longest_len / 30.0))
            return best_match_code, best_match_name, best_alias, confidence

        return None, None, None, 0.0

    def is_general_operations_query(self, normalized_query: str) -> Tuple[bool, Optional[str]]:
        """Check if query pertains strictly to general statements, downloads, or reports."""
        for alias in GENERAL_OPERATIONS_ALIASES:
            pattern = rf"\b{re.escape(alias)}\b"
            if re.search(pattern, normalized_query, re.IGNORECASE):
                return True, alias
        return False, None

    def resolve(self, raw_query: str) -> ResolvedEntity:
        """Resolve entity, scheme, parameter, ambiguity, and out-of-scope status.
        
        Execution pipeline:
        1. Query normalization
        2. Out-of-scope competitor check (EC-02)
        3. Scheme matching against 5 curated HDFC funds
        4. Parameter domain detection
        5. General operations detection
        6. Ambiguity evaluation (EC-01)
        """
        normalized_q = self.normalize_query(raw_query)

        # 1. Out-of-scope check (EC-02)
        out_of_scope_name = self.detect_out_of_scope(normalized_q)
        if out_of_scope_name:
            param_type, param_str = self.detect_parameter(normalized_q)
            return ResolvedEntity(
                status=ResolutionStatus.OUT_OF_SCOPE,
                out_of_scope_name=out_of_scope_name,
                parameter=param_str,
                parameter_type=param_type,
                raw_query=raw_query,
                confidence=0.95,
            )

        # 2. Scheme match
        scheme_code, scheme_name, matched_alias, conf = self.match_scheme(normalized_q)
        param_type, param_str = self.detect_parameter(normalized_q)

        # 3. If scheme is resolved
        if scheme_code:
            return ResolvedEntity(
                status=ResolutionStatus.RESOLVED,
                scheme_code=scheme_code,
                scheme_name=scheme_name,
                parameter=param_str,
                parameter_type=param_type,
                confidence=conf,
                matched_alias=matched_alias,
                raw_query=raw_query,
            )

        # 4. Check for General Operations queries
        is_ops, ops_alias = self.is_general_operations_query(normalized_q)
        if is_ops and ("how to" in normalized_q or "download" in normalized_q or "statement" in normalized_q or "capital gains" in normalized_q or "report" in normalized_q):
            return ResolvedEntity(
                status=ResolutionStatus.GENERAL_OPERATIONS,
                scheme_code="general-operations",
                scheme_name="General Mutual Fund Operations",
                parameter=param_str or "operations",
                parameter_type=param_type if param_type != ParameterType.UNKNOWN else ParameterType.OPERATIONS,
                confidence=0.90,
                matched_alias=ops_alias,
                raw_query=raw_query,
            )

        # 5. Ambiguity Interception (EC-01):
        # If user asks about a parameter (exit load, SIP, TER, lock-in, tax) without naming any scheme
        if param_type in [
            ParameterType.EXPENSE_RATIO,
            ParameterType.EXIT_LOAD,
            ParameterType.INVESTMENT_LIMITS,
            ParameterType.LOCK_IN_PERIOD,
            ParameterType.TAXATION,
            ParameterType.FUND_OVERVIEW,
        ]:
            return ResolvedEntity(
                status=ResolutionStatus.AMBIGUOUS_SCHEME,
                parameter=param_str,
                parameter_type=param_type,
                is_ambiguous=True,
                confidence=0.85,
                raw_query=raw_query,
            )

        # 6. Fallback: Unknown status for generic or unstructured semantic queries
        return ResolvedEntity(
            status=ResolutionStatus.UNKNOWN,
            parameter=param_str,
            parameter_type=param_type,
            raw_query=raw_query,
            confidence=0.30,
        )

    def get_supported_schemes_list(self) -> List[Dict[str, str]]:
        """Return list of supported schemes with name, category, and canonical URL."""
        return [
            {
                "scheme_code": code,
                "scheme_name": info["name"],
                "category": info["category"],
                "canonical_url": info["canonical_url"],
            }
            for code, info in self.schemes_map.items()
        ]
