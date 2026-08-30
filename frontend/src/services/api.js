/**
 * API Service for interacting with FastAPI Backend endpoints.
 */

const rawBase = (import.meta.env.VITE_API_BASE_URL || '').trim();
// Clean base URL: remove trailing slashes and redundant '/api/v1' suffix if accidentally supplied
const API_BASE = rawBase.replace(/\/+$/, '').replace(/\/api\/v1$/, '');

export async function sendChatQuery(query) {
  const response = await fetch(`${API_BASE}/api/v1/chat/query`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query }),
  });

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    if (response.status === 405) {
      throw new Error(
        'Request failed with status 405 (Method Not Allowed). The request was routed to a static host or unsupported endpoint. If running locally, please ensure the FastAPI backend is running on http://localhost:8000. If deployed, ensure VITE_API_BASE_URL is configured to your live backend.'
      );
    }
    throw new Error(errorBody.detail || `Request failed with status ${response.status}`);
  }

  return response.json();
}

export async function fetchSchemes() {
  const response = await fetch(`${API_BASE}/api/v1/schemes`);
  if (!response.ok) {
    throw new Error(`Failed to fetch schemes (HTTP ${response.status})`);
  }
  return response.json();
}

export async function fetchHealth() {
  const response = await fetch(`${API_BASE}/api/v1/health`);
  if (!response.ok) {
    throw new Error(`Failed to fetch health (HTTP ${response.status})`);
  }
  return response.json();
}

export async function fetchRateLimits() {
  const response = await fetch(`${API_BASE}/api/v1/rate-limit`);
  if (!response.ok) {
    throw new Error(`Failed to fetch rate limits (HTTP ${response.status})`);
  }
  return response.json();
}
