const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/bluebridge';

const jsonHeaders = {
  'Content-Type': 'application/json',
};

async function request(path, options = {}) {
  const url = `${API_BASE_URL}${path}`;
  const token = localStorage.getItem('access');
  const headers = {
    ...jsonHeaders,
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...(options.headers || {}),
  };
  const config = { ...options, headers };

  const response = await fetch(url, config);
  if (!response.ok) {
    let detail = '';
    try {
      const errJson = await response.clone().json();
      // 토큰 불일치/만료 시 토큰 초기화
      if (errJson?.code === 'token_not_valid') {
        localStorage.removeItem('access');
        localStorage.removeItem('refresh');
        localStorage.removeItem('username');
        localStorage.removeItem('is_staff');
        detail = '로그인이 만료되었습니다. 다시 로그인해 주세요.';
        window.location.reload();
      } else if (errJson?.detail) {
        detail = typeof errJson.detail === 'string' ? errJson.detail : JSON.stringify(errJson.detail);
      } else if (errJson && Object.keys(errJson).length) {
        detail = JSON.stringify(errJson);
      }
    } catch (_) {
      // fallback to text
      detail = await response.text();
    }
    throw new Error(detail || `Request failed: ${response.status}`);
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

// 추천
export async function fetchRecommendList() {
  return request('/recommend/');
}

export async function fetchRecommendDetail(query) {
  return request('/recommend/detail/', {
    method: 'POST',
    body: JSON.stringify({ query }),
  });
}

export async function fetchProfile() {
  // 현재 사용자 프로필은 /profile/me/ 엔드포인트에서 조회
  return request('/profile/me/');
}

export async function saveProfile(profile) {
  // 프로필 업데이트는 /profile/me/ 엔드포인트로 전송
  return request('/profile/me/', {
    method: 'PUT',
    body: JSON.stringify(profile),
  });
}

export async function fetchWishlist() {
  return request('/policies/wishlist/');
}

export async function createWishlist(policyId) {
  return request('/policies/wishlist/', {
    method: 'POST',
    body: JSON.stringify({ policy_id: policyId }),
  });
}

export async function deleteWishlist(policyId) {
  return request(`/policies/wishlist/${policyId}/`, {
    method: 'DELETE',
  });
}

export async function login(payload) {
  return request('/auth/login/', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function signup(payload) {
  return request('/auth/signup/', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function checkUsername(username) {
  const params = new URLSearchParams({ username });
  return request(`/auth/check-username/?${params.toString()}`);
}

// boards
export async function fetchBoards() {
  return request('/boards/');
}

export async function fetchBoardById(id) {
  return request(`/boards/${id}/`);
}

export async function createBoard(payload) {
  return request('/boards/', {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function updateBoard(id, payload) {
  return request(`/boards/${id}/`, {
    method: 'PUT',
    body: JSON.stringify(payload),
  });
}

export async function deleteBoard(id) {
  return request(`/boards/${id}/`, {
    method: 'DELETE',
  });
}

export async function createComment(boardId, payload) {
  return request(`/boards/${boardId}/comments/`, {
    method: 'POST',
    body: JSON.stringify(payload),
  });
}

export async function deleteComment(commentId) {
  return request(`/boards/comments/${commentId}/`, {
    method: 'DELETE',
  });
}

export async function toggleBoardLike(boardId) {
  return request(`/boards/${boardId}/like/`, {
    method: 'POST',
  });
}
