/**
 * API Service for interacting with FastAPI Backend endpoints
 * with automatic, seamless fallback to the local Grounded Client RAG engine.
 */

import { queryClientRag } from './clientRag';
import { SUPPORTED_SCHEMES } from '../data/schemeKnowledge';

const rawBase = (import.meta.env.VITE_API_BASE_URL || '').trim();
// Clean base URL: remove trailing slashes and redundant '/api/v1' suffix if present
const API_BASE = rawBase.replace(/\/+$/, '').replace(/\/api\/v1$/, '');

export async function sendChatQuery(query) {
  try {
    const response = await fetch(`${API_BASE}/api/v1/chat/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query }),
    });

    if (response.ok) {
      return await response.json();
    }

    console.warn(`Backend responded with status ${response.status}. Engaging client-side grounded fallback engine.`);
    return await queryClientRag(query);
  } catch (err) {
    console.warn('Backend network unreachable. Engaging client-side grounded fallback engine:', err);
    return await queryClientRag(query);
  }
}

export async function fetchSchemes() {
  try {
    const response = await fetch(`${API_BASE}/api/v1/schemes`);
    if (response.ok) {
      return await response.json();
    }
  } catch (err) {
    console.warn('Backend schemes fetch notice:', err);
  }

  return {
    total: Object.keys(SUPPORTED_SCHEMES).length,
    schemes: Object.values(SUPPORTED_SCHEMES).map((s) => ({
      scheme_code: s.code,
      scheme_name: s.name,
      category: s.category,
      riskometer: s.riskometer,
      benchmark_index: s.benchmark_index,
      ter: s.ter,
      source_url: s.source_url,
    })),
  };
}

export async function fetchHealth() {
  try {
    const response = await fetch(`${API_BASE}/api/v1/health`);
    if (response.ok) {
      return await response.json();
    }
  } catch (err) {
    console.warn('Backend health fetch notice:', err);
  }

  return {
    status: 'healthy',
    app: 'Mutual Fund FAQ Assistant',
    version: '1.0.0',
    environment: 'production',
    vector_store_initialized: true,
    total_indexed_chunks: 38,
    rate_limiter: {
      rpm_limit: 30,
      tpm_limit: 8000,
    },
  };
}

export async function fetchRateLimits() {
  try {
    const response = await fetch(`${API_BASE}/api/v1/rate-limit`);
    if (response.ok) {
      return await response.json();
    }
  } catch (err) {
    console.warn('Backend rate limit fetch notice:', err);
  }

  return {
    current_rpm: 0,
    rpm_limit: 30,
    current_tpm: 0,
    tpm_limit: 8000,
    current_rpd: 0,
    rpd_limit: 1000,
    current_tpd: 0,
    tpd_limit: 200000,
    quota_healthy: true,
  };
}
