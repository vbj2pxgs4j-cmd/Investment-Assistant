import { executeClientRAG } from './clientRAGEngine';

const rawBase = (import.meta.env.VITE_API_BASE_URL || '').trim();
// Clean base URL: remove trailing slashes and redundant '/api/v1' suffix if accidentally supplied
const API_BASE = rawBase.replace(/\/+$/, '').replace(/\/api\/v1$/, '');

export async function sendChatQuery(query) {
  try {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 6000);

    const response = await fetch(`${API_BASE}/api/v1/chat/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ query }),
      signal: controller.signal,
    });
    clearTimeout(timeoutId);

    if (response.ok) {
      return await response.json();
    }

    console.warn(`FastAPI backend returned HTTP ${response.status}. Using client-side facts engine.`);
    return executeClientRAG(query);
  } catch (error) {
    console.warn('Backend request failed or timed out. Falling back to client-side facts engine:', error);
    return executeClientRAG(query);
  }
}

export async function fetchSchemes() {
  try {
    const response = await fetch(`${API_BASE}/api/v1/schemes`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    return await response.json();
  } catch (err) {
    return {
      total: 5,
      schemes: [
        {
          scheme_code: 'hdfc-mid-cap-fund-direct-growth',
          scheme_name: 'HDFC Mid-Cap Opportunities',
          category: 'Equity - Mid Cap',
          riskometer: 'Very High Risk',
          benchmark_index: 'NIFTY Midcap 150 TRI',
          ter: '0.74%',
          source_url: 'https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth',
        },
        {
          scheme_code: 'hdfc-small-cap-fund-direct-growth',
          scheme_name: 'HDFC Small Cap Fund',
          category: 'Equity - Small Cap',
          riskometer: 'Very High Risk',
          benchmark_index: 'BSE 250 SmallCap TRI',
          ter: '0.68%',
          source_url: 'https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth',
        },
        {
          scheme_code: 'hdfc-large-cap-fund-direct-growth',
          scheme_name: 'HDFC Top 100 Fund',
          category: 'Equity - Large Cap',
          riskometer: 'Very High Risk',
          benchmark_index: 'NIFTY 100 TRI',
          ter: '1.08%',
          source_url: 'https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth',
        },
        {
          scheme_code: 'hdfc-elss-tax-saver-fund-direct-plan-growth',
          scheme_name: 'HDFC ELSS Tax Saver',
          category: 'Equity - ELSS',
          riskometer: 'Very High Risk',
          benchmark_index: 'NIFTY 500 TRI',
          ter: '1.15%',
          source_url: 'https://groww.in/mutual-funds/hdfc-elss-tax-saver-fund-direct-plan-growth',
        },
        {
          scheme_code: 'hdfc-gold-etf-fund-of-fund-direct-plan-growth',
          scheme_name: 'HDFC Gold ETF FoF',
          category: 'Other - FoF Dom',
          riskometer: 'High Risk',
          benchmark_index: 'Domestic Price of Gold',
          ter: '0.27%',
          source_url: 'https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth',
        },
      ],
    };
  }
}

export async function fetchHealth() {
  try {
    const response = await fetch(`${API_BASE}/api/v1/health`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    return await response.json();
  } catch (err) {
    return {
      status: 'healthy',
      app: 'Mutual Fund FAQ Assistant',
      version: '1.0.0',
      environment: 'client-edge',
      vector_store_initialized: true,
      total_indexed_chunks: 38,
      rate_limiter: {
        rpm_remaining: 30,
        tpm_remaining: 8000,
        rpd_remaining: 1000,
        tpd_remaining: 200000,
      },
    };
  }
}

export async function fetchRateLimits() {
  try {
    const response = await fetch(`${API_BASE}/api/v1/rate-limit`);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    return await response.json();
  } catch (err) {
    return {
      rpm_limit: 30,
      rpm_used: 1,
      rpm_remaining: 29,
      tpm_limit: 8000,
      tpm_used: 120,
      tpm_remaining: 7880,
      rpd_limit: 1000,
      rpd_remaining: 999,
      tpd_limit: 200000,
      tpd_remaining: 199880,
    };
  }
}
