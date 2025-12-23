import { defineStore } from 'pinia';
import { ref } from 'vue';
import {
  fetchPolicies,
  fetchPolicyById,
  fetchRecommendations,
  fetchRagRecommendations,
} from '../api/client';
import { mockPolicies } from '../data/mockPolicies';

const toPeriod = (start, end) => {
  if (!start && !end) return '제한없음';
  if (start && end) return `${start} ~ ${end}`;
  return start || end || '제한없음';
};

const toAgeRange = (minAge, maxAge) => {
  if (minAge === '제한없음' || maxAge === '제한없음') return '제한없음';
  if (!minAge && !maxAge) return '제한없음';
  if (minAge && maxAge) return `${minAge}-${maxAge}`;
  if (minAge) return `${minAge}+`;
  return `${maxAge}-`;
};

const formatMultiline = (text = '') => {
  const raw = (text || '').toString();
  if (!raw) return '';
  return raw
    .replace(/\r\n|\r/g, '\n')
    .replace(/\\n/g, '\n')
    .replace(/n\//g, '\n')
    .replace(/\n{2,}/g, '\n')
    .trim();
};

const cleanList = (items = []) => {
  const seen = new Set();
  const result = [];
  items.forEach((item) => {
    const raw = (item || '').toString().trim();
    if (!raw) return;
    const stripped = raw.replace(/^[-/]+/, '').replace(/[-/]+$/, '').trim();
    if (!stripped || seen.has(stripped)) return;
    seen.add(stripped);
    result.push(stripped);
  });
  return result;
};

const transformPolicy = (p) => {
  if (!p) return null;

  const region = p.region_sigungu || p.region_sido || '전국';

  const eligibilitySections = [
    { label: '취업·직업', values: p.employment_requirements || p.employment || [] },
    { label: '학력', values: p.education_requirements || p.education || [] },
    { label: '전공', values: p.major_requirements || p.major || [] },
    { label: '지원대상', values: p.special_target || [] },
  ];

  const eligibility = eligibilitySections.flatMap((section) => {
    const cleaned = cleanList(section.values).map(formatMultiline);
    if (!cleaned.length) return [`${section.label}: 제한없음`];
    return cleaned.map((v) => `${section.label}: ${v}`);
  });

  return {
    id: p.id ?? p.source_id ?? p.sourceId ?? String(Math.random()),
    title: p.title || '',
    category: p.category || p.source || '',
    organization: p.provider || '',
    description: formatMultiline(p.summary || ''),
    eligibility,
    benefits: formatMultiline(p.policy_detail || p.apply_method || ''),
    applicationPeriod: toPeriod(p.start_date, p.end_date),
    ageRange: toAgeRange(p.min_age, p.max_age),
    region,
    employmentStatus: p.employment_requirements || [],
    tags: cleanList([
      p.category || '',
      ...(Array.isArray(p.target_detail) ? p.target_detail.filter((v) => v && v !== '/') : []),
      ...(Array.isArray(p.keywords) ? p.keywords : []),
    ]),
    uxScore: p.ux_score ?? null,
    profileScore: p.profile_score ?? null,
    querySimilarity: p.query_similarity ?? null,
    detailLink:
      (Array.isArray(p.detail_links) && p.detail_links[0]) ||
      p.detail_link ||
      (typeof p.detail_links === 'string' ? p.detail_links : ''),
    raw: p,
  };
};

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
        setPolicies(data.map(transformPolicy).filter(Boolean));
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
        const mapped = transformPolicy(data) || data;
        const existingIndex = policies.value.findIndex((p) => String(p.id) === String(id));
        if (existingIndex > -1) {
          policies.value[existingIndex] = mapped;
        } else {
          policies.value.push(mapped);
        }
        return mapped;
      }
    } catch (err) {
      error.value = err.message || '정책 상세를 불러오지 못했습니다.';
      return getById(id);
    } finally {
      loading.value = false;
    }
    return null;
  };

  const recommendPolicies = async () => {
    loading.value = true;
    error.value = null;
    try {
      const data = await fetchRecommendations();
      if (Array.isArray(data)) {
        return data.map(transformPolicy).filter(Boolean);
      }
    } catch (err) {
      error.value = err.message || '추천 결과를 불러오지 못했습니다.';
    } finally {
      loading.value = false;
    }
    return [];
  };

  const recommendPoliciesRag = async (query) => {
    if (!query || !query.trim()) return { results: [], top3: [], distances: [] };
    loading.value = true;
    error.value = null;
    try {
      const data = await fetchRagRecommendations(query.trim());
      const results = Array.isArray(data?.results) ? data.results.map(transformPolicy).filter(Boolean) : [];
      return {
        results,
        top3: Array.isArray(data?.top3) ? data.top3 : [],
        distances: Array.isArray(data?.distances) ? data.distances : [],
      };
    } catch (err) {
      error.value = err.message || 'AI 추천을 불러오지 못했습니다.';
      return { results: [], top3: [], distances: [] };
    } finally {
      loading.value = false;
    }
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
    recommendPoliciesRag,
    searchPolicies,
  };
});
