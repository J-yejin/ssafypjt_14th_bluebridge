const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/bluebridge';

const jsonHeaders = {
  'Content-Type': 'application/json',
};

async function request(path, options = {}) {
  const url = `${API_BASE_URL}${path}`;
  const config = {
    headers: jsonHeaders,
    ...options,
  };

  const response = await fetch(url, config);
  if (!response.ok) {
    const errorText = await response.text();
    throw new Error(errorText || `Request failed: ${response.status}`);
  }
  if (response.status === 204) return null;
  return response.json();
}

export async function fetchPolicies(params = {}) {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== '') {
      searchParams.append(key, value);
    }
  });
  const query = searchParams.toString();
  const suffix = query ? `?${query}` : '';
  return request(`/policies/${suffix}`);
}

export async function fetchPolicyById(id) {
  return request(`/policies/${id}/`);
}

export async function fetchRecommendations(payload) {
  return request('/policies/recommend/', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function fetchProfile() {
  return request('/profile/');
}

export async function saveProfile(profile) {
  return request('/profile/', {
    method: 'POST',
    body: JSON.stringify(profile),
  });
}
