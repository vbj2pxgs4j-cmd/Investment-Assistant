/**
 * API Service for interacting with FastAPI Backend endpoints.
 */

const API_BASE = ''; // Uses relative URLs with Vite dev proxy or same-origin in prod

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
