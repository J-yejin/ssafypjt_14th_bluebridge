import { defineStore } from 'pinia';
import { ref, computed } from 'vue';

export const useAuthStore = defineStore('auth', () => {
  const access = ref(localStorage.getItem('access') || '');
  const refresh = ref(localStorage.getItem('refresh') || '');

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

  const clearTokens = () => {
    access.value = '';
    refresh.value = '';
    localStorage.removeItem('access');
    localStorage.removeItem('refresh');
  };

  return {
    access,
    refresh,
    isAuthenticated,
    setTokens,
    clearTokens,
  };
});
