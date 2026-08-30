/**
 * Client-Side Deterministic Facts & Guardrail Engine
 * Provides immediate zero-downtime offline and static hosting (Vercel) fallback
 * adhering strictly to facts-only, <= 3 sentences, canonical Groww citations, and compliance guardrails.
 */

const SCHEMES_FACTS = {
  'hdfc-mid-cap-fund-direct-growth': {
    name: 'HDFC Mid-Cap Opportunities Fund',
    short_name: 'HDFC Mid-Cap',
    code: 'hdfc-mid-cap-fund-direct-growth',
    category: 'Equity: Mid Cap',
    benchmark: 'NIFTY Midcap 150 TRI',
    riskometer: 'Very High',
    url: 'https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth',
    ter_direct: '0.74%',
    ter_regular: '1.48%',
    exit_load: '1.00% if redeemed or switched out within 1 year (365 days) from allotment, and Nil after 1 year.',
    lock_in: 'Nil. There is no lock-in period as this is an open-ended equity fund.',
    min_sip: '₹100 per installment',
    min_lump_sum: '₹100',
    taxation: 'STCG is taxed at 20% if redeemed within 12 months. LTCG above ₹1.25 Lakh per financial year is taxed at 12.5% without indexation if held for over 12 months.',
    statement: 'Statements can be downloaded via Groww App (Profile > Reports) or the HDFC MF online investor portal using PAN and Folio number.',
    last_updated: '2026-08-30',
  },
  'hdfc-small-cap-fund-direct-growth': {
    name: 'HDFC Small Cap Fund',
    short_name: 'HDFC Small Cap',
    code: 'hdfc-small-cap-fund-direct-growth',
    category: 'Equity: Small Cap',
    benchmark: 'BSE 250 SmallCap TRI',
    riskometer: 'Very High',
    url: 'https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth',
    ter_direct: '0.68%',
    ter_regular: '1.54%',
    exit_load: '1.00% if redeemed within 1 year (365 days) from allotment, and Nil after 1 year.',
    lock_in: 'Nil. There is no statutory lock-in period as this is an open-ended equity fund.',
    min_sip: '₹100 per installment',
    min_lump_sum: '₹100',
    taxation: 'STCG is taxed at 20% if redeemed within 12 months. LTCG above ₹1.25 Lakh per fiscal year is taxed at 12.5% without indexation if held for over 12 months.',
    statement: 'Download account statements directly from the Groww App (Profile > Reports) or via the HDFC MF investor portal.',
    last_updated: '2026-08-30',
  },
  'hdfc-large-cap-fund-direct-growth': {
    name: 'HDFC Top 100 Fund',
    short_name: 'HDFC Top 100',
    code: 'hdfc-large-cap-fund-direct-growth',
    category: 'Equity: Large Cap',
    benchmark: 'NIFTY 100 TRI',
    riskometer: 'Very High',
    url: 'https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth',
    ter_direct: '1.08%',
    ter_regular: '1.63%',
    exit_load: '1.00% if redeemed within 30 days from allotment, and Nil after 30 days.',
    lock_in: 'Nil. There is no lock-in period as this is an open-ended large-cap equity fund.',
    min_sip: '₹100 per installment',
    min_lump_sum: '₹100',
    taxation: 'STCG is taxed at 20% if redeemed within 12 months. LTCG above ₹1.25 Lakh per financial year is taxed at 12.5% without indexation for holdings over 12 months.',
    statement: 'Download your statement and capital gains summary on the Groww App under Profile > Reports or via the HDFC AMC investor portal.',
    last_updated: '2026-08-30',
  },
  'hdfc-elss-tax-saver-fund-direct-plan-growth': {
    name: 'HDFC ELSS Tax Saver Fund',
    short_name: 'HDFC ELSS Tax Saver',
    code: 'hdfc-elss-tax-saver-fund-direct-plan-growth',
    category: 'Equity: ELSS (Tax Saving)',
    benchmark: 'NIFTY 500 TRI',
    riskometer: 'Very High',
    url: 'https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth',
    ter_direct: '1.15%',
    ter_regular: '1.74%',
    exit_load: 'Nil. No exit load is applicable, but units cannot be redeemed before completing the mandatory 3-year lock-in period.',
    lock_in: '3 years (36 months) mandatory statutory lock-in from the date of each SIP installment or lump sum allotment under Section 80C (Old Tax Regime).',
    min_sip: '₹500 per installment',
    min_lump_sum: '₹500',
    taxation: 'Investments qualify for tax deduction up to ₹1.5 Lakh under Section 80C (Old Tax Regime). LTCG above ₹1.25 Lakh upon redemption after 3 years is taxed at 12.5% without indexation.',
    statement: 'Tax deduction (80C) certificates and statements are downloadable from the Groww App (Profile > Reports > Tax Reports) or HDFC MF online.',
    last_updated: '2026-08-30',
  },
  'hdfc-gold-etf-fund-of-fund-direct-plan-growth': {
    name: 'HDFC Gold ETF Fund of Fund',
    short_name: 'HDFC Gold ETF FoF',
    code: 'hdfc-gold-etf-fund-of-fund-direct-plan-growth',
    category: 'Other: Fund of Funds (Domestic Gold)',
    benchmark: 'Domestic Price of Physical Gold',
    riskometer: 'High',
    url: 'https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth',
    ter_direct: '0.27%',
    ter_regular: '0.58%',
    exit_load: '2.00% if redeemed within 15 days from allotment, and Nil after 15 days.',
    lock_in: 'Nil. There is no lock-in period for this domestic commodities fund of fund.',
    min_sip: '₹100 per installment',
    min_lump_sum: '₹100',
    taxation: 'Gains are taxed at applicable individual income tax slab rates as per debt and non-equity mutual fund tax regulations (Post April 1, 2023).',
    statement: 'Statements can be accessed via Groww (Reports section) or generated on the HDFC Mutual Fund investor website using your registered PAN.',
    last_updated: '2026-08-30',
  },
};

const DEFAULT_GROWW_URL = 'https://groww.in/mutual-funds';
const DEFAULT_DISCLAIMER = 'Facts-only. No investment advice.';
const DEFAULT_DATE = '2026-08-30';

// PII Patterns
const PII_PATTERNS = [
  /[A-Z]{5}[0-9]{4}[A-Z]/i, // PAN
  /\b[2-9]\d{3}[\s-]?[0-9]{4}[\s-]?[0-9]{4}\b/, // Aadhaar
  /\b(?:\+91[\s-]?)?[6-9]\d{9}\b/, // Phone
  /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b/, // Email
  /\b(?:otp|verification code|pin)\b[^\d\n]{0,25}\b([0-9]{4,8})\b/i, // OTP
];

// Refusal Patterns
const ADVISORY_TERMS = [
  'should i buy', 'should i invest', 'recommend', 'which fund is best', 'best mutual fund',
  'is it good to invest', 'advice me', 'suggest me', 'give advice', 'portfolio review',
  'will it double', 'guaranteed return', 'predict return', 'future return', 'safe to invest'
];

const COMPARISON_TERMS = [
  'compare', 'which one is better', 'vs', 'versus', 'which fund is better', 'better than'
];

const LIVE_NAV_TERMS = [
  'live nav', 'current nav', 'today nav', 'latest nav price', 'realtime nav', 'market price'
];

/**
 * Execute client-side deterministic facts query
 */
export function executeClientRAG(query) {
  const cleanQuery = (query || '').trim();
  const lower = cleanQuery.toLowerCase();
  const startTime = performance.now();

  // 1. PII Check
  for (const pattern of PII_PATTERNS) {
    if (pattern.test(cleanQuery)) {
      return {
        status: 'blocked',
        query: cleanQuery,
        intent: 'pii_detected',
        response: 'Security Notice: Your query contains sensitive personal or financial identification details (e.g., PAN, Aadhaar, phone, OTP, or account information). To protect your privacy and security, personal data is blocked and will not be processed or stored. Please submit queries without personal credentials.',
        sentence_count: 3,
        source_url: DEFAULT_GROWW_URL,
        last_updated: DEFAULT_DATE,
        disclaimer: DEFAULT_DISCLAIMER,
        is_fallback: true,
        latency_ms: Math.round(performance.now() - startTime),
      };
    }
  }

  // 2. Intent Routing - Advisory & Comparison Refusals
  if (ADVISORY_TERMS.some((term) => lower.includes(term))) {
    return {
      status: 'refusal',
      query: cleanQuery,
      intent: 'advisory',
      response: 'I cannot provide investment recommendations, fund rankings, or financial advice. I am a facts-only assistant designed to answer objective scheme parameters and operational queries. Please consult a SEBI-registered investment advisor or explore verified factsheets on Groww.',
      sentence_count: 3,
      source_url: DEFAULT_GROWW_URL,
      last_updated: DEFAULT_DATE,
      disclaimer: DEFAULT_DISCLAIMER,
      is_fallback: true,
      latency_ms: Math.round(performance.now() - startTime),
    };
  }

  if (COMPARISON_TERMS.some((term) => lower.includes(term))) {
    return {
      status: 'refusal',
      query: cleanQuery,
      intent: 'comparison',
      response: 'I cannot provide comparative investment rankings or advise which fund is better for your portfolio. I can provide objective factual parameters such as expense ratios, exit loads, and minimum SIP limits for individual schemes. Please explore verified scheme factsheets on Groww.',
      sentence_count: 3,
      source_url: DEFAULT_GROWW_URL,
      last_updated: DEFAULT_DATE,
      disclaimer: DEFAULT_DISCLAIMER,
      is_fallback: true,
      latency_ms: Math.round(performance.now() - startTime),
    };
  }

  if (LIVE_NAV_TERMS.some((term) => lower.includes(term))) {
    return {
      status: 'refusal',
      query: cleanQuery,
      intent: 'live_nav_price',
      response: 'Live Net Asset Value (NAV) fluctuates daily based on market closing prices and is published at the end of each business day. This assistant provides static factsheet parameters and does not stream real-time price feeds. Please check current NAV and real-time portfolio valuation directly on Groww.',
      sentence_count: 3,
      source_url: DEFAULT_GROWW_URL,
      last_updated: DEFAULT_DATE,
      disclaimer: DEFAULT_DISCLAIMER,
      is_fallback: true,
      latency_ms: Math.round(performance.now() - startTime),
    };
  }

  // 3. Scheme Matching
  let targetScheme = null;
  if (lower.includes('mid') || lower.includes('midcap') || lower.includes('mid-cap') || lower.includes('opportunities')) {
    targetScheme = SCHEMES_FACTS['hdfc-mid-cap-fund-direct-growth'];
  } else if (lower.includes('small') || lower.includes('smallcap') || lower.includes('small-cap')) {
    targetScheme = SCHEMES_FACTS['hdfc-small-cap-fund-direct-growth'];
  } else if (lower.includes('top 100') || lower.includes('large') || lower.includes('large cap') || lower.includes('large-cap') || lower.includes('top100')) {
    targetScheme = SCHEMES_FACTS['hdfc-large-cap-fund-direct-growth'];
  } else if (lower.includes('elss') || lower.includes('tax') || lower.includes('80c') || lower.includes('tax saver')) {
    targetScheme = SCHEMES_FACTS['hdfc-elss-tax-saver-fund-direct-plan-growth'];
  } else if (lower.includes('gold') || lower.includes('etf') || lower.includes('fof') || lower.includes('commodity')) {
    targetScheme = SCHEMES_FACTS['hdfc-gold-etf-fund-of-fund-direct-plan-growth'];
  }

  // 4. Parameter Resolution
  if (targetScheme) {
    const isExitLoad = lower.includes('exit') || lower.includes('load') || lower.includes('penalty') || lower.includes('redemption fee');
    const isLockIn = lower.includes('lock') || lower.includes('lock-in') || lower.includes('lockin') || lower.includes('holding period') || lower.includes('tenure');
    const isSip = lower.includes('sip') || lower.includes('minimum') || lower.includes('min') || lower.includes('lump') || lower.includes('investment limit') || lower.includes('installment');
    const isTer = lower.includes('ter') || lower.includes('expense') || lower.includes('ratio') || lower.includes('fee') || lower.includes('charges');
    const isTax = lower.includes('tax') || lower.includes('stcg') || lower.includes('ltcg') || lower.includes('capital gains');
    const isBenchmark = lower.includes('benchmark') || lower.includes('index') || lower.includes('riskometer') || lower.includes('category');
    const isStatement = lower.includes('statement') || lower.includes('download') || lower.includes('folio') || lower.includes('cas') || lower.includes('account');

    let facts = [];

    // Multi-parameter inquiry handling (e.g. exit load + lock-in + SIP)
    if (isExitLoad) {
      facts.push(`The exit load for ${targetScheme.name} is ${targetScheme.exit_load}`);
    }
    if (isLockIn) {
      facts.push(`The lock-in period is ${targetScheme.lock_in}`);
    }
    if (isSip) {
      facts.push(`The minimum SIP investment is ${targetScheme.min_sip}, and minimum lump sum is ${targetScheme.min_lump_sum}.`);
    }
    if (isTer && !isExitLoad) {
      facts.push(`The Total Expense Ratio (TER) is ${targetScheme.ter_direct} for Direct Plan and ${targetScheme.ter_regular} for Regular Plan.`);
    }
    if (isTax && !isLockIn) {
      facts.push(`Taxation: ${targetScheme.taxation}`);
    }
    if (isBenchmark && facts.length === 0) {
      facts.push(`${targetScheme.name} belongs to ${targetScheme.category} benchmarked against ${targetScheme.benchmark} with a ${targetScheme.riskometer} riskometer rating.`);
    }
    if (isStatement && facts.length === 0) {
      facts.push(targetScheme.statement);
    }

    if (facts.length === 0) {
      // General overview
      facts.push(`${targetScheme.name} (${targetScheme.category}) has an expense ratio of ${targetScheme.ter_direct} and minimum SIP of ${targetScheme.min_sip}.`);
      facts.push(`Exit load is ${targetScheme.exit_load}`);
      facts.push(`Benchmarked against ${targetScheme.benchmark}.`);
    }

    // Ensure strictly <= 3 sentences
    const answerText = facts.slice(0, 3).join(' ');

    return {
      status: 'success',
      query: cleanQuery,
      intent: 'factual',
      response: answerText,
      sentence_count: Math.min(3, facts.length),
      source_url: targetScheme.url,
      last_updated: targetScheme.last_updated,
      disclaimer: DEFAULT_DISCLAIMER,
      is_fallback: true,
      latency_ms: Math.round(performance.now() - startTime),
    };
  }

  // General statement or operations query without specific scheme
  if (lower.includes('statement') || lower.includes('download') || lower.includes('folio') || lower.includes('cas')) {
    return {
      status: 'success',
      query: cleanQuery,
      intent: 'operations',
      response: 'Account statements and capital gains reports can be downloaded online from the Groww App under Profile > Reports > Mutual Fund Statements. You can also generate consolidated account statements (CAS) or visit the HDFC Mutual Fund investor portal using your PAN and Folio number. Registered folio numbers are visible in your Groww portfolio dashboard.',
      sentence_count: 3,
      source_url: DEFAULT_GROWW_URL,
      last_updated: DEFAULT_DATE,
      disclaimer: DEFAULT_DISCLAIMER,
      is_fallback: true,
      latency_ms: Math.round(performance.now() - startTime),
    };
  }

  // Ambiguous scheme prompt
  return {
    status: 'disambiguation',
    query: cleanQuery,
    intent: 'ambiguous_scheme',
    response: 'Mutual fund parameters vary by scheme across equity, commodities, and tax-saving categories. Please specify which of the 5 supported HDFC schemes you are inquiring about: HDFC Mid-Cap Opportunities, HDFC Small Cap, HDFC Top 100, HDFC ELSS Tax Saver, or HDFC Gold ETF FoF. You can also browse all verified scheme details on Groww.',
    sentence_count: 3,
    source_url: DEFAULT_GROWW_URL,
    last_updated: DEFAULT_DATE,
    disclaimer: DEFAULT_DISCLAIMER,
    is_fallback: true,
    latency_ms: Math.round(performance.now() - startTime),
  };
}
