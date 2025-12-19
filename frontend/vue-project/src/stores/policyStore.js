import { defineStore } from 'pinia';
import { ref } from 'vue';
import { fetchPolicies, fetchPolicyById, fetchRecommendations } from '../api/client';
import { mockPolicies } from '../data/mockPolicies';

export const usePolicyStore = defineStore('policy', () => {
  const policies = ref([...mockPolicies]);
  const loading = ref(false);
  const error = ref(null);

  const setPolicies = (list) => {
    policies.value = list || [];
  };

  const getById = (id) => policies.value.find((p) => String(p.id) === String(id));

  const loadPolicies = async (filters = {}) => {
    loading.value = true;
    error.value = null;
    try {
      const data = await fetchPolicies(filters);
      if (Array.isArray(data)) {
        setPolicies(data);
      }
    } catch (err) {
      error.value = err.message || '정책 목록을 불러오지 못했습니다.';
      if (!policies.value.length) {
        setPolicies(mockPolicies);
      }
    } finally {
      loading.value = false;
    }
  };

  const loadPolicyById = async (id) => {
    loading.value = true;
    error.value = null;
    try {
      const data = await fetchPolicyById(id);
      if (data) {
        const existingIndex = policies.value.findIndex((p) => String(p.id) === String(id));
        if (existingIndex > -1) {
          policies.value[existingIndex] = data;
        } else {
          policies.value.push(data);
        }
        return data;
      }
    } catch (err) {
      error.value = err.message || '정책 정보를 불러오지 못했습니다.';
      return getById(id);
    } finally {
      loading.value = false;
    }
    return null;
  };

  const recommendPolicies = async (payload) => {
    loading.value = true;
    error.value = null;
    try {
      const data = await fetchRecommendations(payload);
      if (Array.isArray(data)) {
        return data;
      }
    } catch (err) {
      error.value = err.message || '추천 결과를 불러오지 못했습니다.';
      // fallback: simple filtering by interests + region
      const interests = (payload?.interests || []).map((v) => v.toLowerCase());
      return policies.value.filter((policy) => {
        const tagMatch = interests.length
          ? policy.tags.some((tag) => interests.includes(tag.toLowerCase()))
          : true;
        const regionMatch = payload?.region ? policy.region === payload.region || policy.region === '전국' : true;
        return tagMatch && regionMatch;
      });
    } finally {
      loading.value = false;
    }
    return [];
  };

  const searchPolicies = (query) => {
    if (!query) return [];
    const lower = query.toLowerCase();
    return policies.value
      .map((policy) => {
        let score = 0;
        if (policy.title.toLowerCase().includes(lower)) score += 3;
        if (policy.description.toLowerCase().includes(lower)) score += 2;
        if (policy.tags.some((tag) => tag.toLowerCase().includes(lower))) score += 2;
        if (policy.category.toLowerCase().includes(lower)) score += 1;
        return { policy, score };
      })
      .filter((item) => item.score > 0)
      .sort((a, b) => b.score - a.score)
      .map((item) => item.policy)
      .slice(0, 6);
  };

  return {
    policies,
    loading,
    error,
    setPolicies,
    getById,
    loadPolicies,
    loadPolicyById,
    recommendPolicies,
    searchPolicies,
  };
});
