import { defineStore } from 'pinia';
import { ref, reactive } from 'vue';
import {
  fetchPolicies,
  fetchPolicyById,
  fetchRecommendDetail,
  fetchRecommendList,
  fetchWishlist,
  createWishlist,
  deleteWishlist,
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
    .replace(/n\//g, '\n') // handle n/ markers as new lines
    .replace(/[■□▪▫▣◾◽◼◻※]/g, '\n$& ') // keep bullet/box symbols but move to a new line
    .replace(/\s*-\s*/g, '\n- ') // break dash-separated bullets into new lines
    .replace(/\n{2,}/g, '\n') // collapse multiple blank lines
    .trim();
};

const cleanList = (items = []) => {
  const seen = new Set();
  const result = [];
  items.forEach((item) => {
    const raw = (item || '').toString().trim();
    if (!raw) return;
    // 선행/후행 대시·슬래시 제거 (예: "-/도내 청년 누구나" -> "도내 청년 누구나")
    const stripped = raw.replace(/^[-/]+/, '').replace(/[-/]+$/, '').trim();
    if (!stripped) return;
    if (seen.has(stripped)) return;
    seen.add(stripped);
    result.push(stripped);
  });
  return result;
};

const transformPolicy = (p) => {
  if (!p) return null;

  const mapRegionsToBuckets = (applicableRegions = [], fallback = '') => {
    const topLevel = [
      '서울특별시',
      '부산광역시',
      '대구광역시',
      '인천광역시',
      '광주광역시',
      '대전광역시',
      '울산광역시',
      '세종특별자치시',
      '경기도',
      '강원특별자치도',
      '충청북도',
      '충청남도',
      '전라북도',
      '전라남도',
      '경상북도',
      '경상남도',
      '제주특별자치도',
    ];

    const mapName = (name = '') => {
      const r = String(name || '').trim();
      if (!r) return '';
      if (r.includes('전국')) return '전국';
      const found = topLevel.find((t) => r.includes(t));
      return found || r;
    };

    const regions = Array.isArray(applicableRegions) ? applicableRegions : [];
    const cleaned = [];
    const seen = new Set();
    regions.map(mapName).filter(Boolean).forEach((r) => {
      if (seen.has(r)) return;
      seen.add(r);
      cleaned.push(r);
    });
    if (cleaned.length) return cleaned;

    const fb = mapName(fallback);
    return fb ? [fb] : ['전국'];
  };

  const mapToBucket = (value = '') => {
    const v = value.trim();
    const bucketMap = {
      일자리: '일자리',
      취업: '일자리',
      창업: '일자리',
      교육: '교육',
      '문화·여가': '복지문화',
      복지문화: '복지문화',
      신체건강: '건강',
      정신건강: '건강',
      생활지원: '생활지원',
      보육: '생활지원',
      '보호·돌봄': '생활지원',
      서민금융: '재무/법률',
      법률: '재무/법률',
      '안전·위기': '위기·안전',
      '임신·출산': '가족/권리',
      '입양·위탁': '가족/권리',
      참여권리: '가족/권리',
      주거: '생활지원',
    };
    return bucketMap[v] || '';
  };

  const rawCategory = p.category || '';
  const rawCategoryParts = rawCategory
    .split(',')
    .map((v) => v.trim())
    .filter(Boolean);
  const mappedCategories = cleanList(rawCategoryParts.map(mapToBucket).filter(Boolean));
  const category = mappedCategories[0] || '기타';

  const region = p.region_sigungu || p.region_sido || '';
  const regionBuckets = mapRegionsToBuckets(p.applicable_regions, region);

  const eligibilitySections = [
    { label: '취업·직업', values: p.employment_requirements || p.employment || [] },
    { label: '학력', values: p.education_requirements || p.education || [] },
    { label: '전공', values: p.major_requirements || p.major || [] },
    { label: '지원대상', values: p.special_target || [] },
  ];

  const eligibility = eligibilitySections.flatMap((section) => {
    const cleaned = cleanList(section.values).map(formatMultiline);
    if (!cleaned.length) return [`${section.label} | 제한없음`];
    return cleaned.map((v) => `${section.label}: ${v}`);
  });

  return {
    id: p.id ?? p.source_id ?? p.sourceId ?? String(Math.random()),
    title: p.title || '',
    category,
    categories: mappedCategories,
    organization: p.provider || '',
    description: formatMultiline(p.summary || ''),
    eligibility,
    benefits: formatMultiline(p.policy_detail || p.apply_method || ''),
    applicationPeriod: toPeriod(p.start_date, p.end_date),
    ageRange: toAgeRange(p.min_age, p.max_age),
    region: regionBuckets[0],
    regionBucket: regionBuckets[0],
    regionBuckets,
    employmentStatus: p.employment_requirements || [],
    tags: cleanList([
      category,
      ...(Array.isArray(p.target_detail) ? p.target_detail.filter((v) => v && v !== '/') : []),
    ]),
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
  const pagination = ref({ count: 0, next: null, previous: null, page_size: 20 });
  const wishlistIds = ref([]);
  const hasLoaded = ref(false);
  const browseState = reactive({
    searchTerm: '',
    selectedCategory: '',
    selectedRegion: '',
    sortBy: 'title',
    showFilters: false,
  });

  const setPolicies = (list) => {
    policies.value = list || [];
  };

  const getById = (id) => policies.value.find((p) => String(p.id) === String(id));

  const loadPolicies = async (filters = {}, options = {}) => {
    const { force = true } = options; // 기본적으로 항상 새로 불러온다
    loading.value = true;
    error.value = null;
    try {
      const data = await fetchPolicies(filters);
      let items = data;
      if (data && Array.isArray(data.results)) {
        items = data.results;
        pagination.value = {
          count: data.count || 0,
          next: data.next || null,
          previous: data.previous || null,
          page_size: filters.page_size || 20,
        };
      } else {
        pagination.value = {
          count: Array.isArray(items) ? items.length : 0,
          next: null,
          previous: null,
          page_size: filters.page_size || 20,
        };
      }
      if (Array.isArray(items)) {
        setPolicies(items.map(transformPolicy).filter(Boolean));
      }
    } catch (err) {
      error.value = err.message || '정책 목록을 불러오지 못했습니다';
      if (!policies.value.length) {
        setPolicies(mockPolicies);
      }
    } finally {
      loading.value = false;
      hasLoaded.value = true;
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
      error.value = err.message || '정책 상세를 불러오지 못했습니다';
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
      const data = await fetchRecommendList();
      if (Array.isArray(data)) {
        return data.map(transformPolicy).filter(Boolean);
      }
    } catch (err) {
      error.value = err.message || '추천 결과를 불러오지 못했습니다';
      return [];
    } finally {
      loading.value = false;
    }
    return [];
  };

  const recommendPoliciesByQuery = async (query) => {
    loading.value = true;
    error.value = null;
    try {
      const data = await fetchRecommendDetail(query);
      const results = Array.isArray(data?.results)
        ? data.results.map(transformPolicy).filter(Boolean)
        : [];
      const top3 = Array.isArray(data?.top3) ? data.top3 : [];
      return { results, top3 };
    } catch (err) {
      error.value = err.message || '추천 결과를 불러오지 못했습니다';
      return { results: [], top3: [] };
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

  const loadWishlist = async () => {
    try {
      const data = await fetchWishlist();
      const ids = Array.isArray(data)
        ? data
            .map((item) => item?.policy?.id ?? item?.policy_id ?? item?.policy)
            .filter((id) => id !== undefined && id !== null)
            .map((id) => String(id))
        : [];
      wishlistIds.value = ids;
    } catch (_) {
      wishlistIds.value = [];
    }
  };

  const isWishlisted = (policyId) => wishlistIds.value.includes(String(policyId));

  const addToWishlist = async (policyId) => {
    await createWishlist(policyId);
    const id = String(policyId);
    if (!wishlistIds.value.includes(id)) {
      wishlistIds.value = [...wishlistIds.value, id];
    }
  };

  const removeFromWishlist = async (policyId) => {
    await deleteWishlist(policyId);
    const id = String(policyId);
    wishlistIds.value = wishlistIds.value.filter((item) => item !== id);
  };

  const toggleWishlist = async (policyId) => {
    if (isWishlisted(policyId)) {
      await removeFromWishlist(policyId);
    } else {
      await addToWishlist(policyId);
    }
  };

  return {
    policies,
    loading,
    error,
    hasLoaded,
    browseState,
    pagination,
    setPolicies,
    getById,
    loadPolicies,
    loadPolicyById,
    recommendPolicies,
    recommendPoliciesByQuery,
    searchPolicies,
    loadWishlist,
    isWishlisted,
    addToWishlist,
    removeFromWishlist,
    toggleWishlist,
  };
});
