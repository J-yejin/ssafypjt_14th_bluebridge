import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const useAuthStore = defineStore('auth', () => {
  const access = ref(localStorage.getItem('access') || '');
  const refresh = ref(localStorage.getItem('refresh') || '');
  const username = ref(localStorage.getItem('username') || '');

  const parseJwtPayload = (token = '') => {
    try {
      const [, payload] = token.split('.');
      if (!payload) return null;
      const base64 = payload.replace(/-/g, '+').replace(/_/g, '/');
      const padded = base64 + '='.repeat((4 - (base64.length % 4)) % 4);
      return JSON.parse(atob(padded));
    } catch (_) {
      return null;
    }
  };

  const isTokenExpired = (token = '') => {
    if (!token) return true;
    const payload = parseJwtPayload(token);
    if (!payload?.exp) return false;
    const now = Math.floor(Date.now() / 1000);
    return payload.exp <= now;
  };

  const isAuthenticated = computed(() => Boolean(access.value));

  const setTokens = (tokens = {}) => {
    if (tokens.access) {
      access.value = tokens.access;
      localStorage.setItem('access', tokens.access);
    }
    if (tokens.refresh) {
      refresh.value = tokens.refresh;
      localStorage.setItem('refresh', tokens.refresh);
    }
  };

  const setUsername = (name = '') => {
    username.value = name || '';
    if (name) {
      localStorage.setItem('username', name);
    } else {
      localStorage.removeItem('username');
    }
  };

  const clearTokens = () => {
    access.value = '';
    refresh.value = '';
    username.value = '';
    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
    localStorage.removeItem('username');
  };

  const validateTokens = () => {
    if (access.value && isTokenExpired(access.value)) {
      clearTokens();
    }
  };

  return {
    access,
    refresh,
    username,
    isAuthenticated,
    setTokens,
    setUsername,
    clearTokens,
    validateTokens,
  };
});
