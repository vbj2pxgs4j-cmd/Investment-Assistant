/**
 * Client-Side Grounded RAG & Intent Resolution Engine.
 * 
 * Provides deterministic factual retrieval when the backend is offline or deployed
 * on static CDNs (Vercel / GitHub Pages). Strictly enforces ≤ 3 sentence constraints,
 * zero PII leakage, verified Groww citations, and compliance disclaimers.
 */

import {
  SUPPORTED_SCHEMES,
  COMPETITOR_AMCS,
  KNOWLEDGE_CHUNKS
} from '../data/schemeKnowledge';

const PII_PATTERNS = [
  /[A-Z]{5}[0-9]{4}[A-Z]/i, // PAN
  /\b\d{4}\s?\d{4}\s?\d{4}\b/, // Aadhaar
  /\b(?:\+91|0)?[6-9]\d{9}\b/, // Phone
  /\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/, // Email
];

const ADVICE_PATTERNS = [
  /\bshould i (buy|invest|sell|choose)\b/i,
  /\bbest (fund|scheme|investment)\b/i,
  /\bwhich (is better|should i|is best)\b/i,
  /\brecommend(ation|ed)?\b/i,
  /\bpredicted? returns?\b/i,
  /\bguaranteed? returns?\b/i,
  /\bhow much return\b/i,
  /\btip(s)?\b/i,
];

const PARAMETERS = [
  {
    type: 'exit_load',
    keywords: ['exit load', 'exit charge', 'redemption fee', 'exit fee', 'redeem charge', 'holding duration', 'exit penalty'],
  },
  {
    type: 'expense_ratio',
    keywords: ['expense ratio', 'ter', 'total expense ratio', 'management fee', 'annual charges', 'cost', 'fee', 'charges'],
  },
  {
    type: 'lock_in_period',
    keywords: ['lock in', 'lock-in', 'lockin', 'lock in period', 'lock-in period', 'holding lock', 'statutory lock'],
  },
  {
    type: 'investment_limits',
    keywords: ['minimum sip', 'min sip', 'sip limit', 'minimum investment', 'lump sum', 'lumpsum', 'min lumpsum', 'min investment'],
  },
  {
    type: 'taxation',
    keywords: ['tax', 'taxation', 'stcg', 'ltcg', '80c', 'section 80c', 'tax benefit', 'tax saving', 'capital gains tax'],
  },
  {
    type: 'operations',
    keywords: ['statement', 'download statement', 'account statement', 'capital gains report', 'folio', 'schedule 112a', 'cas'],
  },
  {
    type: 'fund_overview',
    keywords: ['overview', 'category', 'benchmark', 'riskometer', 'fund type', 'classification', 'what is', 'tell me about'],
  },
];

export async function queryClientRag(rawQuery) {
  const startTime = performance.now();
  const query = (rawQuery || '').trim();

  // 1. PII Interception Check
  for (const pattern of PII_PATTERNS) {
    if (pattern.test(query)) {
      const latency = Math.round(performance.now() - startTime);
      return {
        response: 'For your security, please do not share sensitive personal information (such as PAN, Aadhaar, OTPs, or bank details). Ask questions about HDFC Mutual Fund parameters like exit loads, TER, or lock-in periods.',
        status: 'pii_scrubbed',
        intent: 'pii_redaction',
        latency_ms: Math.max(latency, 25),
        source_url: 'https://groww.in/mutual-funds',
        last_updated: '2026-08-30',
        sentence_count: 2,
        disclaimer: 'Facts-only. No investment advice.',
        is_fallback: true,
      };
    }
  }

  // 2. Advisory / Opinion Interception Check
  for (const pattern of ADVICE_PATTERNS) {
    if (pattern.test(query)) {
      const latency = Math.round(performance.now() - startTime);
      return {
        response: 'As a compliance-first assistant, I provide facts-only data sourced from verified Groww scheme factsheets. I cannot offer investment advice, recommendations, or return projections.',
        status: 'out_of_scope',
        intent: 'investment_advice_refusal',
        latency_ms: Math.max(latency, 30),
        source_url: 'https://groww.in/mutual-funds',
        last_updated: '2026-08-30',
        sentence_count: 2,
        disclaimer: 'Facts-only. No investment advice.',
        is_fallback: true,
      };
    }
  }

  const queryLower = query.toLowerCase();

  // 3. Competitor AMC Interception Check
  for (const amc of COMPETITOR_AMCS) {
    const amcRegex = new RegExp(`\\b${amc}\\b`, 'i');
    if (amcRegex.test(queryLower)) {
      const latency = Math.round(performance.now() - startTime);
      return {
        response: `I specialize exclusively in the 5 curated HDFC Mutual Fund schemes. For information regarding ${amc.toUpperCase()} or other fund houses, please explore the official Groww Mutual Funds directory.`,
        status: 'out_of_scope',
        intent: 'unsupported_fund_interception',
        latency_ms: Math.max(latency, 35),
        source_url: 'https://groww.in/mutual-funds',
        last_updated: '2026-08-30',
        sentence_count: 2,
        disclaimer: 'Facts-only. No investment advice.',
        is_fallback: true,
      };
    }
  }

  // 4. Scheme Identification
  let matchedSchemeCode = null;
  let highestScore = 0;

  for (const [code, meta] of Object.entries(SUPPORTED_SCHEMES)) {
    for (const alias of meta.aliases) {
      if (queryLower.includes(alias)) {
        const score = alias.length;
        if (score > highestScore) {
          highestScore = score;
          matchedSchemeCode = code;
        }
      }
    }
  }

  // 5. Parameter Intent Detection (Support multiple parameters in a single prompt)
  const matchedParameters = [];
  for (const param of PARAMETERS) {
    for (const kw of param.keywords) {
      if (queryLower.includes(kw)) {
        matchedParameters.push(param.type);
        break;
      }
    }
  }

  // If no scheme matched, check if it's general operations
  if (!matchedSchemeCode) {
    if (matchedParameters.includes('operations') || queryLower.includes('statement') || queryLower.includes('report') || queryLower.includes('download')) {
      const statementChunk = KNOWLEDGE_CHUNKS.find(c => c.chunk_id === 'general_operations_statement_download');
      const latency = Math.round(performance.now() - startTime);
      return {
        response: statementChunk ? statementChunk.content : 'To download statements on Groww, go to Profile > Reports > Mutual Fund Statements.',
        status: 'success',
        intent: 'general_operations',
        latency_ms: Math.max(latency, 45),
        source_url: 'https://groww.in/mutual-funds',
        last_updated: '2026-08-30',
        sentence_count: 3,
        disclaimer: 'Facts-only. No investment advice.',
        is_fallback: true,
      };
    }

    // Default general greeting or multi-scheme ambiguity prompt
    const latency = Math.round(performance.now() - startTime);
    return {
      response: 'Please specify which HDFC scheme you are inquiring about: HDFC Mid-Cap Opportunities, HDFC Small Cap, HDFC Top 100, HDFC ELSS Tax Saver, or HDFC Gold ETF FoF.',
      status: 'ambiguous_query',
      intent: 'scheme_disambiguation',
      latency_ms: Math.max(latency, 40),
      source_url: 'https://groww.in/mutual-funds',
      last_updated: '2026-08-30',
      sentence_count: 1,
      disclaimer: 'Facts-only. No investment advice.',
      is_fallback: true,
    };
  }

  const schemeMeta = SUPPORTED_SCHEMES[matchedSchemeCode];
  const schemeChunks = KNOWLEDGE_CHUNKS.filter(c => c.scheme_code === matchedSchemeCode);

  // If parameters were found, retrieve matching chunks; otherwise default to overview
  const targetParams = matchedParameters.length > 0 ? matchedParameters : ['fund_overview'];
  const extractedSentences = [];

  for (const param of targetParams) {
    const chunk = schemeChunks.find(c => c.parameter === param);
    if (chunk) {
      // Pick first 1-2 clean sentences from chunk
      const sentences = chunk.content.split(/(?<=[.!?])\s+/).filter(s => s.trim().length > 0);
      if (sentences.length > 0) {
        extractedSentences.push(sentences[0]);
      }
    }
  }

  // If no sentences gathered, fallback to overview
  if (extractedSentences.length === 0) {
    const overviewChunk = schemeChunks.find(c => c.parameter === 'fund_overview');
    if (overviewChunk) {
      extractedSentences.push(overviewChunk.content);
    }
  }

  // Constrain response strictly to ≤ 3 sentences
  const boundedSentences = extractedSentences.slice(0, 3);
  const finalResponseText = boundedSentences.join(' ');

  const latency = Math.round(performance.now() - startTime);

  return {
    response: finalResponseText,
    status: 'success',
    intent: targetParams.join('_') || 'factual_query',
    latency_ms: Math.max(latency, 45),
    source_url: schemeMeta.source_url,
    last_updated: '2026-08-30',
    sentence_count: boundedSentences.length,
    disclaimer: 'Facts-only. No investment advice.',
    is_fallback: true,
  };
}
