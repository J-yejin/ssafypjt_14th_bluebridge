import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const useAuthStore = defineStore('auth', () => {
  const access = ref(localStorage.getItem('access') || '');
  const refresh = ref(localStorage.getItem('refresh') || '');
  const username = ref(localStorage.getItem('username') || '');

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

  return {
    access,
    refresh,
    username,
    isAuthenticated,
    setTokens,
    setUsername,
    clearTokens,
  };
});
