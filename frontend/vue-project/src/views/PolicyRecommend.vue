<template>
  <div class="min-h-screen">
    <!-- 로그인 안내 -->
    <div v-if="!isLoggedIn" class="min-h-screen flex items-center justify-center">
      <div class="max-w-2xl mx-auto px-8 lg:px-12">
        <div class="bg-white rounded-3xl shadow-2xl p-12 text-center">
          <div class="w-24 h-24 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6 shadow-lg">
            <AlertCircle :size="48" class="text-blue-600" />
          </div>
          <h2 class="text-blue-900 mb-4 text-3xl">로그인이 필요해요</h2>
          <p class="text-gray-600 mb-8 text-lg leading-relaxed">
            맞춤 추천을 받으려면 먼저 로그인하고 프로필을 완성해 주세요.
          </p>
          <button
            type="button"
            @click="goLogin"
            class="inline-flex items-center gap-3 bg-gradient-to-r from-blue-500 to-cyan-500 text-white px-10 py-4 rounded-2xl hover:shadow-2xl transition-all text-lg shadow-lg"
          >
            <span>로그인하러 가기</span>
            <ArrowRight :size="24" />
          </button>
        </div>
      </div>
    </div>

    <!-- 프로필 미완성 안내 -->
    <div v-else-if="!userStore.isProfileComplete" class="min-h-screen flex items-center justify-center">
      <div class="max-w-2xl mx-auto px-8 lg:px-12">
        <div class="bg-white rounded-3xl shadow-2xl p-12 text-center">
          <div class="w-24 h-24 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-6 shadow-lg">
            <AlertCircle :size="48" class="text-yellow-600" />
          </div>
          <h2 class="text-blue-900 mb-4 text-3xl">프로필을 완성해주세요</h2>
          <p class="text-gray-600 mb-8 text-lg leading-relaxed">
            맞춤 추천을 위해 추가 정보가 필요합니다.
            <br />
            간단히 입력하면 AI가 바로 추천해드려요.
          </p>
          <button
            type="button"
            @click="goOnboarding"
            class="inline-flex items-center gap-3 bg-gradient-to-r from-blue-500 to-cyan-500 text-white px-10 py-4 rounded-2xl hover:shadow-2xl transition-all text-lg shadow-lg"
          >
            <span>프로필 카드 작성</span>
            <ArrowRight :size="24" />
          </button>
        </div>
      </div>
    </div>

    <!-- 추천 화면 -->
    <div v-else class="max-w-[1400px] mx-auto px-8 lg:px-12 py-12">
      <div class="mb-12">
        <h1 class="text-blue-900 mb-3 text-4xl">정책 추천</h1>
        <p class="text-gray-600 text-lg">프로필을 기반으로 맞춤 정책을 추천해 드립니다.</p>
      </div>

      <!-- RAG Search -->
      <div class="bg-white rounded-2xl shadow-xl p-10 mb-12 border border-blue-100">
        <div class="flex items-start justify-between gap-4 mb-6">
          <div class="w-12 h-12 bg-gradient-to-br from-cyan-400 to-cyan-600 rounded-xl flex items-center justify-center flex-shrink-0 shadow-md">
            <Sparkles :size="24" class="text-white" />
          </div>
          <div class="flex-1">
            <h2 class="text-blue-900 mb-2 text-2xl flex items-center gap-3">
              AI 정책 검색
              <span
                v-if="ragLoading"
                class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-gradient-to-r from-cyan-100 to-blue-100 text-cyan-700 text-sm border border-cyan-200 shadow-sm"
              >
                <span class="w-2 h-2 rounded-full bg-cyan-500 animate-pulse" />
                검색 중입니다
              </span>
            </h2>
            <p class="text-gray-600 text-lg">키워드나 조건을 입력하면 AI가 관련 정책을 찾아줍니다.</p>
          </div>
        </div>
        <div class="flex gap-6">
          <input
            type="text"
            placeholder="예) 청년 창업 지원, 주거 보증금 대출"
            v-model="ragQuery"
            @keypress.enter="handleRagSearch"
            class="flex-1 px-6 py-4 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-cyan-500 focus:border-transparent text-lg"
          />
          <button
            @click="handleRagSearch"
            class="bg-gradient-to-r from-cyan-500 to-blue-500 text-white px-10 py-4 rounded-xl hover:shadow-2xl transition-all flex items-center gap-3 text-lg shadow-lg"
          >
            <Sparkles :size="24" />
            <span>검색</span>
          </button>
        </div>
        <div class="mt-3 text-sm text-gray-500 flex flex-wrap gap-3">
          <span class="text-gray-600">예시:</span>
          <button
            v-for="example in ['등록금 지원 대학생', '서울 청년 월세 지원', '창업 자금 보증', '저소득층 의료비 지원']"
            :key="example"
            type="button"
            class="px-3 py-1 rounded-full bg-gray-100 text-gray-600 hover:bg-gray-200 transition"
            @click="ragQuery = example; handleRagSearch();"
          >
            {{ example }}
          </button>
        </div>
        <p class="mt-2 text-xs text-gray-500">
          대상·분야·혜택·지역을 함께 적으면 더 정확한 결과를 받을 수 있어요. (예: “서울 청년 전세 대출”, “학자금 대출 이자 지원”)
        </p>
      </div>

      <!-- RAG Results -->
      <div v-if="showRagResults || ragLoading" class="mb-12">
        <div v-if="ragLoading" class="flex items-center gap-3 mb-4">
          <span class="px-4 py-2 bg-cyan-50 text-cyan-700 rounded-full text-sm shadow-sm">검색 중입니다</span>
        </div>
        <div v-if="showRagResults && ragBasedRecommendations.length > 0">
          <div class="flex items-center gap-3 mb-6">
            <h2 class="text-blue-900 text-3xl">AI 추천 결과</h2>
            <span
              v-if="ragLoading"
              class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-gradient-to-r from-cyan-100 to-blue-100 text-cyan-700 text-sm border border-cyan-200 shadow-sm"
            >
              <span class="w-2 h-2 rounded-full bg-cyan-500 animate-pulse" />
              검색 중입니다
            </span>
          </div>
          <div class="grid lg:grid-cols-2 gap-8">
            <router-link
              v-for="policy in ragBasedRecommendations"
              :key="policy.id"
              :to="`/policy/${policy.id}`"
              @click="persistRecommendations"
              class="bg-gradient-to-br from-cyan-50 to-blue-50 rounded-2xl shadow-lg hover:shadow-2xl transition-all p-8 border-2 border-cyan-200 hover:border-cyan-300 group relative overflow-hidden"
            >
              <div class="absolute top-0 right-0 w-32 h-32 bg-cyan-200/30 rounded-full -mr-16 -mt-16" />
              <div class="relative">
                <div class="flex items-center gap-3 mb-4">
                  <Sparkles :size="20" class="text-cyan-600" />
                  <span class="text-cyan-700">AI 추천</span>
                </div>
                <div class="flex items-start justify-between mb-4">
                  <div class="flex items-center gap-3">
                    <span class="px-4 py-1.5 bg-cyan-100 text-cyan-700 rounded-full">
                      {{ policy.category }}
                    </span>
                    <span class="text-gray-500">{{ policy.organization }}</span>
                  </div>
                  <button
                    type="button"
                    class="inline-flex items-center justify-center w-10 h-10 rounded-full border border-cyan-200 text-cyan-700 hover:text-rose-500 hover:border-rose-200 transition bg-white cursor-pointer/70 cursor-pointer"
                    :class="policyStore.isWishlisted(policy.id) ? 'text-rose-500 border-rose-200 bg-rose-50' : ''"
                    @click.stop.prevent="handleToggleWishlist(policy.id)"
                    aria-label="&#44288;&#49900;&#32;&#51221;&#52293;"
                    title="&#44288;&#49900;&#32;&#51221;&#52293;"
                  >
                    <Heart
                      class="w-5 h-5"
                      :class="policyStore.isWishlisted(policy.id) ? 'text-rose-500' : ''"
                      :fill="policyStore.isWishlisted(policy.id) ? '#ef4444' : 'none'"
                      :stroke="policyStore.isWishlisted(policy.id) ? '#ef4444' : 'currentColor'"
                    />
                  </button>
                </div>
                <div class="flex items-center justify-between gap-3 mb-3">
                  <h3 class="text-blue-900 text-2xl group-hover:text-blue-700 transition-colors">{{ policy.title }}</h3>
                  <span
                    v-if="formatScore(policy.raw?.similarity_score_10 ?? policy.raw?.query_similarity)"
                    class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/60 text-cyan-700 text-sm border border-cyan-200 shadow-sm"
                  >
                    <Sparkles :size="16" class="text-cyan-500" />
                    적합도 {{ formatScore(policy.raw?.similarity_score_10 ?? policy.raw?.query_similarity) }}
                  </span>
                </div>

                <div class="flex flex-wrap gap-2 mb-4">
                  <span v-for="tag in policy.tags" :key="tag" class="px-3 py-1 bg-white/60 text-gray-600 rounded-lg text-sm">
                    #{{ tag }}
                  </span>
                </div>

                <div
                  v-if="ragReasonMap[String(policy.id)]"
                  class="mt-4 px-4 py-3 bg-white/70 rounded-xl border border-cyan-100 text-gray-700 text-sm leading-relaxed"
                >
                  <span class="font-semibold text-cyan-700">추천 이유</span>
                  <span class="mx-2 text-gray-400">•</span>
                  <span>{{ ragReasonMap[String(policy.id)] }}</span>
                </div>
              </div>
            </router-link>
          </div>
        </div>
        <div
          v-else-if="showRagResults && !ragLoading"
          class="bg-white rounded-2xl p-12 text-center shadow-md border border-cyan-100"
        >
          <div class="w-20 h-20 bg-cyan-50 rounded-full flex items-center justify-center mx-auto mb-4">
            <Search :size="40" class="text-cyan-400" />
          </div>
          <p class="text-gray-600 text-lg mb-2">출력된 결과가 없습니다.</p>
          <p class="text-gray-400">다른 키워드로 다시 검색해 보세요.</p>
        </div>
      </div>

      <!-- Profile-based Recommendations -->
      <div>
        <div class="flex items-center gap-3 mb-6">
          <h2 class="text-blue-900 text-3xl">프로필 기반 추천</h2>
          <span
            v-if="profileLoading"
            class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-gradient-to-r from-blue-100 to-cyan-100 text-blue-700 text-sm border border-blue-200 shadow-sm"
          >
            <span class="w-2 h-2 rounded-full bg-blue-500 animate-pulse" />
            추천 준비 중입니다
          </span>
        </div>
        <div v-if="profileLoading" class="flex items-center gap-3 mb-4"></div>
        <div v-else-if="profileBasedRecommendations.length > 0" class="grid lg:grid-cols-2 gap-8">
          <router-link
            v-for="policy in profileBasedRecommendations"
            :key="policy.id"
            :to="`/policy/${policy.id}`"
            @click="persistRecommendations"
            class="bg-white rounded-2xl shadow-md hover:shadow-xl transition-all p-8 border-2 border-transparent hover:border-blue-200 group"
          >
            <div class="flex items-start justify-between mb-4">
              <div class="flex items-center gap-3">
                <span class="px-4 py-1.5 bg-blue-100 text-blue-700 rounded-full">
                  {{ policy.category }}
                </span>
                <span class="text-gray-500">{{ policy.organization }}</span>
              </div>
              <div class="flex items-center gap-2">
                <span class="text-gray-500 bg-gray-50 px-3 py-1 rounded-full text-sm">{{ policy.region }}</span>
                <button
                  type="button"
                  class="inline-flex items-center justify-center w-10 h-10 rounded-full border border-gray-200 text-gray-500 hover:text-rose-500 hover:border-rose-200 transition bg-white cursor-pointer"
                  :class="policyStore.isWishlisted(policy.id) ? 'text-rose-500 border-rose-200 bg-rose-50' : ''"
                  @click.stop.prevent="handleToggleWishlist(policy.id)"
                  aria-label="&#44288;&#49900;&#32;&#51221;&#52293;"
                  title="&#44288;&#49900;&#32;&#51221;&#52293;"
                >
                  <Heart
                    class="w-5 h-5"
                    :class="policyStore.isWishlisted(policy.id) ? 'text-rose-500' : ''"
                    :fill="policyStore.isWishlisted(policy.id) ? '#ef4444' : 'none'"
                    :stroke="policyStore.isWishlisted(policy.id) ? '#ef4444' : 'currentColor'"
                  />
                </button>
              </div>
            </div>
            <div class="flex items-center justify-between gap-3 mb-3">
              <h3 class="text-blue-900 text-2xl group-hover:text-blue-700 transition-colors">{{ policy.title }}</h3>
              <span
                v-if="formatScore(policy.raw?.profile_score_10 ?? policy.raw?.ux_score)"
                class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-50 text-blue-700 text-sm border border-blue-200 shadow-sm"
              >
                <Sparkles :size="16" class="text-blue-500" />
                적합도 {{ formatScore(policy.raw?.profile_score_10 ?? policy.raw?.ux_score) }}
              </span>
            </div>

            <div class="flex flex-wrap gap-2 mb-4">
              <span v-for="tag in policy.tags" :key="tag" class="px-3 py-1 bg-gray-100 text-gray-600 rounded-lg text-sm">
                #{{ tag }}
              </span>
            </div>

            <div
              v-if="profileReasonMap[String(policy.id)]"
              class="mt-4 px-4 py-3 bg-blue-50 rounded-xl border border-blue-100 text-gray-700 text-sm leading-relaxed"
            >
              <span class="font-semibold text-blue-700">추천 이유</span>
              <span class="mx-2 text-gray-400">•</span>
              <span>{{ profileReasonMap[String(policy.id)] }}</span>
            </div>
          </router-link>
        </div>
        <div v-else class="bg-white rounded-2xl p-16 text-center shadow-md">
          <div class="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Search :size="40" class="text-gray-400" />
          </div>
          <p class="text-gray-500 text-lg mb-2">출력된 결과가 없습니다.</p>
          <p class="text-gray-400 mb-6">관심사나 지역을 바꿔 다시 요청해 보세요.</p>
          <router-link
            to="/profile/edit"
            class="inline-flex items-center gap-2 bg-gradient-to-r from-blue-500 to-cyan-500 text-white px-6 py-3 rounded-xl hover:shadow-lg transition-all text-base shadow-md"
          >
            나의 프로필로 이동
            <ArrowRight :size="18" />
          </router-link>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter, onBeforeRouteLeave } from 'vue-router';
import { Sparkles, AlertCircle, Search, ArrowRight, Heart } from 'lucide-vue-next';
import { useUserStore } from '../stores/userStore';
import { usePolicyStore } from '../stores/policyStore';
import { useAuthStore } from '../stores/authStore';

const router = useRouter();
const authStore = useAuthStore();
const userStore = useUserStore();
const policyStore = usePolicyStore();

const isLoggedIn = computed(() => authStore.isAuthenticated);

const ragQuery = ref('');
const showRagResults = ref(false);
const ragBasedRecommendations = ref([]);
const ragLoading = ref(false);
const ragMeta = ref({});
const recommendedFromApi = ref([]);
const profileLoading = ref(false);
const profileMeta = ref({});
const hasRestored = ref(false);
const RAG_STORAGE_KEY = 'bb_rag_recommendations';
const PROFILE_STORAGE_KEY = 'bb_profile_recommendations';
const PROFILE_REFRESH_KEY = 'bb_profile_refresh';
const ragReasonMap = computed(() => {
  const map = {};
  ragBasedRecommendations.value.forEach((item) => {
    if (item?.reason) map[String(item.id)] = item.reason;
  });
  return map;
});
const profileReasonMap = computed(() => {
  const map = {};
  recommendedFromApi.value.forEach((item) => {
    if (item?.reason) map[String(item.id)] = item.reason;
  });
  return map;
});

const loadRecommendations = async () => {
  if (!userStore.isProfileComplete) {
    recommendedFromApi.value = [];
    profileTop3.value = [];
    profileMeta.value = {};
    return;
  }
  profileLoading.value = true;
  try {
    const payload = await policyStore.recommendPolicies();
    recommendedFromApi.value = payload?.results || [];
    profileMeta.value = payload?.meta || {};
  } catch (_) {
    recommendedFromApi.value = [];
    profileMeta.value = {};
  } finally {
    profileLoading.value = false;
  }
};

const persistRecommendations = () => {
  const ragPayload = {
    query: ragQuery.value,
    results: ragBasedRecommendations.value,
    meta: ragMeta.value,
    show: showRagResults.value,
  };
  const profilePayload = {
    results: recommendedFromApi.value,
    meta: profileMeta.value,
  };
  try {
    sessionStorage.setItem(RAG_STORAGE_KEY, JSON.stringify(ragPayload));
    sessionStorage.setItem(PROFILE_STORAGE_KEY, JSON.stringify(profilePayload));
  } catch (_) {
    // ignore storage errors
  }
};

const restoreRecommendations = () => {
  try {
    const ragRaw = sessionStorage.getItem(RAG_STORAGE_KEY);
    const profileRaw = sessionStorage.getItem(PROFILE_STORAGE_KEY);
    let restored = false;
    if (ragRaw) {
      const data = JSON.parse(ragRaw);
      if (Array.isArray(data?.results)) {
        ragBasedRecommendations.value = data.results;
        ragMeta.value = data.meta || {};
        ragQuery.value = data.query || '';
        showRagResults.value = Boolean(data.show);
        restored = true;
      }
    }
    if (profileRaw) {
      const data = JSON.parse(profileRaw);
      if (Array.isArray(data?.results)) {
        recommendedFromApi.value = data.results;
        profileMeta.value = data.meta || {};
        restored = true;
      }
    }
    return restored;
  } catch (_) {
    return false;
  }
};

const initRestore = () => {
  let restored = false;
  try {
    if (sessionStorage.getItem(PROFILE_REFRESH_KEY)) {
      sessionStorage.removeItem(PROFILE_REFRESH_KEY);
      sessionStorage.removeItem(PROFILE_STORAGE_KEY);
    } else {
      restored = restoreRecommendations();
    }
  } catch (_) {
    restored = restoreRecommendations();
  }
  hasRestored.value = restored;
};

initRestore();

onMounted(async () => {
  if (!authStore.isAuthenticated) return;
  await userStore.loadProfile();
  await policyStore.loadWishlist();
  if (!hasRestored.value) {
    policyStore.loadPolicies();
    loadRecommendations();
  }
});

watch(
  () => ({ ...userStore.profile }),
  () => {
    if (!hasRestored.value) {
      loadRecommendations();
    }
  },
  { deep: true }
);

const profileBasedRecommendations = computed(() => {
  if (recommendedFromApi.value.length) return recommendedFromApi.value;
  const list = policyStore.policies || [];
  const interests = (userStore.profile.interests || []).map((i) => i.toLowerCase());
  const region = userStore.profile.region || '';
  const userAge = Number(userStore.profile.age);

  return list.filter((policy) => {
    const [minAge, maxAge] = (policy.ageRange || '').split('-').map(Number);
    const ageMatch = Number.isNaN(userAge)
      ? true
      : (Number.isNaN(minAge) || userAge >= minAge) && (Number.isNaN(maxAge) || userAge <= maxAge);

    const regionMatch = region
      ? !policy.region ||
        policy.region === '전국' ||
        policy.region.includes(region) ||
        region.includes(policy.region)
      : true;

    const interestMatch = interests.length
      ? policy.tags.some((tag) => interests.includes(String(tag).toLowerCase()))
      : true;

    return ageMatch && regionMatch && interestMatch;
  });
});

const handleRagSearch = () => {
  const query = ragQuery.value.trim();
  if (!query) {
    ragBasedRecommendations.value = [];
    ragTop3.value = [];
    showRagResults.value = false;
    ragMeta.value = {};
    return;
  }
  ragLoading.value = true;
  showRagResults.value = true;
  ragMeta.value = {};
  policyStore
    .recommendPoliciesByQuery(query)
    .then(({ results, meta }) => {
      ragBasedRecommendations.value = results || [];
      ragMeta.value = meta || {};
    })
    .catch(() => {
      ragBasedRecommendations.value = [];
      ragMeta.value = {};
    })
    .finally(() => {
      ragLoading.value = false;
    });
};

const formatScore = (score) => {
  if (score === null || score === undefined || score === '') return null;
  const num = Number(score);
  if (Number.isNaN(num)) return null;
  return num.toFixed(1);
};

const goLogin = () => router.push('/login');
const goOnboarding = () => router.push('/onboarding');

const handleToggleWishlist = async (policyId) => {
  if (!authStore.isAuthenticated) {
    alert('로그인 후 이용해주세요.');
    return;
  }
  try {
    await policyStore.toggleWishlist(policyId);
  } catch (err) {
    const message = err?.message || '';
    if (message.toLowerCase().includes('credentials')) {
      alert('로그인 후 이용해주세요.');
      return;
    }
    if (message.toLowerCase().includes('already wishlisted')) {
      await policyStore.loadWishlist();
      return;
    }
    alert(message || '관심정책 처리에 실패했습니다.');
  }
};

onBeforeRouteLeave((to) => {
  if (to.path && to.path.startsWith('/policy/')) {
    return;
  }
  try {
    sessionStorage.removeItem(RAG_STORAGE_KEY);
  } catch (_) {
    // ignore storage errors
  }
  ragQuery.value = '';
  showRagResults.value = false;
  ragBasedRecommendations.value = [];
  ragMeta.value = {};
});
</script>
