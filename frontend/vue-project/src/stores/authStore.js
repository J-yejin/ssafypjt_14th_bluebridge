import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const useAuthStore = defineStore('auth', () => {
  const access = ref(localStorage.getItem('access') || '');
  const refresh = ref(localStorage.getItem('refresh') || '');
  const username = ref(localStorage.getItem('username') || '');

  const parseJwtPayload = (token = '') => {
    const parts = token.split('.');
    if (parts.length < 2) return null;
    try {
      const payload = parts[1].replace(/-/g, '+').replace(/_/g, '/');
      const padded = payload.padEnd(payload.length + ((4 - (payload.length % 4)) % 4), '=');
      return JSON.parse(atob(padded));
    } catch (_) {
      return null;
    }
  };

  const isTokenExpired = (token = '') => {
    const payload = parseJwtPayload(token);
    if (!payload?.exp) return true;
    const now = Math.floor(Date.now() / 1000);
    return payload.exp <= now;
  };

  const isAuthenticated = computed(() => {
    if (!access.value) return false;
    return !isTokenExpired(access.value);
  });

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

  const syncAuthState = () => {
    const storedAccess = localStorage.getItem('access') || '';
    const storedRefresh = localStorage.getItem('refresh') || '';
    const storedUsername = localStorage.getItem('username') || '';

    if (access.value !== storedAccess) access.value = storedAccess;
    if (refresh.value !== storedRefresh) refresh.value = storedRefresh;
    if (username.value !== storedUsername) username.value = storedUsername;

    if (storedAccess && isTokenExpired(storedAccess)) {
      clearTokens();
      return false;
    }
    return Boolean(storedAccess);
  };

  return {
    access,
    refresh,
    username,
    isAuthenticated,
    setTokens,
    setUsername,
    clearTokens,
    syncAuthState,
  };
});
