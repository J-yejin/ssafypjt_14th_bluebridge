const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/bluebridge';

const baseHeaders = { 'Content-Type': 'application/json' };

export async function request(path, options = {}) {
  const token = localStorage.getItem('access');
  const headers = {
    ...baseHeaders,
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers || {}),
  };

  const resp = await fetch(`${API_BASE_URL}${path}`, { ...options, headers });
  if (!resp.ok) {
    let detail = '';
    try {
      const errJson = await resp.clone().json();
      detail = errJson?.detail || errJson?.message || '';
    } catch {
      detail = await resp.text();
    }
    throw new Error(detail || `Request failed: ${resp.status}`);
  }
  if (resp.status === 204) return null;
  return resp.json();
}
