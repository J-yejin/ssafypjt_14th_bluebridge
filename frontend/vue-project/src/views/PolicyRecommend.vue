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
    <div class="max-w-[1400px] mx-auto px-8 lg:px-12 py-12 relative">
      <div class="mb-12">
        <h1 class="text-blue-900 mb-3 text-4xl">정책 추천</h1>
        <p class="text-gray-600 text-lg">프로필을 기반으로 맞춤 정책을 추천해 드립니다.</p>
      </div>

      <!-- RAG Search -->
      <div class="bg-white rounded-2xl shadow-xl p-10 mb-12 border border-blue-100">
        <div class="flex items-start gap-4 mb-4">
          <div class="w-12 h-12 bg-gradient-to-br from-cyan-400 to-cyan-600 rounded-xl flex items-center justify-center flex-shrink-0 shadow-md">
            <Sparkles :size="24" class="text-white" />
          </div>
          <div class="flex-1">
            <h2 class="text-blue-900 mb-2 text-2xl">AI에게 궁금한 정책을 물어보세요</h2>
            <p class="text-gray-600 text-lg">궁금한 내용을 질문하면, 조건에 맞는 정책을 찾아드려요.</p>
          </div>
        </div>
        <div class="flex gap-6">
          <input
            type="text"
            placeholder="궁금한 정책 주제/지원 항목/대상 조건을 입력해보세요"
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
          <div v-if="ragLoading" class="flex items-center gap-2 text-sm text-cyan-700 bg-cyan-50 border border-cyan-100 px-3 py-1.5 rounded-full">
            <Sparkles :size="16" class="animate-pulse" />
            <span>텍스트 검색 추천 찾는 중...</span>
          </div>
        </div>
        <div v-if="queryExamples.length" class="mt-3 flex flex-wrap gap-2 text-sm text-gray-500 items-center">
          <span class="text-gray-400">예시</span>
          <span
            v-for="ex in queryExamples"
            :key="ex"
            class="px-3 py-1 rounded-full bg-blue-50 text-blue-700"
          >
            {{ ex }}
          </span>
        </div>
      </div>

      <!-- Top3 Highlight (사용자 입력 후 노출) -->
      <div v-if="showRagResults && top3Cards.length" class="mb-12">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-blue-500 to-cyan-500 text-white flex items-center justify-center shadow-md">
            <Sparkles :size="18" />
          </div>
          <div>
            <h2 class="text-blue-900 text-2xl">추천 Top3</h2>
            <p class="text-gray-600">적합도와 이유를 간단히 보여드려요.</p>
          </div>
        </div>
        <div class="grid md:grid-cols-3 gap-6">
          <div
            v-for="card in top3Cards"
            :key="card.id"
            class="bg-white rounded-2xl shadow-lg border border-blue-100 p-6 flex flex-col gap-3 hover:-translate-y-1 transition-all"
          >
            <div class="flex items-center justify-between">
              <span class="text-xs font-semibold px-3 py-1 rounded-full bg-blue-50 text-blue-700">추천</span>
            </div>
            <router-link :to="`/policy/${card.id}`" class="text-xl font-semibold text-blue-900 hover:text-blue-700">
              {{ card.title }}
            </router-link>
            <div class="flex flex-wrap gap-2 text-xs text-gray-600">
              <span class="px-2 py-1 rounded-full bg-gray-100">유사도 {{ formatScore(card.similarity_score_10) }}</span>
              <span class="px-2 py-1 rounded-full bg-gray-100">프로필 {{ formatScore(card.profile_score_10) }}</span>
              <span
                v-if="card.policy_target_required"
                :class="[
                  'px-2 py-1 rounded-full',
                  card.policy_target_match ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                ]"
              >
                정책 대상 {{ card.policy_target_match ? '충족' : '미충족' }}
              </span>
            </div>
            <p class="text-gray-600 text-sm leading-relaxed line-clamp-3">
              {{ card.reason || '추천 이유를 불러오는 중입니다.' }}
            </p>
          </div>
        </div>
      </div>

      <!-- RAG Results -->
      <div v-if="showRagResults && ragBasedRecommendations.length > 0" class="mb-12">
        <h2 class="text-blue-900 mb-6 text-3xl">AI 추천 결과</h2>
        <div class="grid lg:grid-cols-2 gap-8">
          <router-link
            v-for="policy in ragBasedRecommendations"
            :key="policy.id"
            :to="`/policy/${policy.id}`"
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
              </div>
              <h3 class="text-blue-900 mb-3 text-2xl group-hover:text-blue-700 transition-colors">{{ policy.title }}</h3>
    
              <div class="flex flex-wrap gap-2">
                <span
                  v-for="tag in policy.tags"
                  :key="tag"
                  class="px-3 py-1 bg-white/60 text-gray-600 rounded-lg text-sm"
                >
                  #{{ tag }}
                </span>
              </div>
            </div>
          </router-link>
        </div>
      </div>

      <!-- Profile-based Recommendations -->
      <div>
        <div class="flex items-center gap-3 mb-3">
          <h2 class="text-blue-900 text-3xl">프로필 기반 추천</h2>
          <div v-if="profileLoading" class="flex items-center gap-2 text-sm text-blue-700 bg-blue-50 border border-blue-100 px-3 py-1.5 rounded-full">
            <Sparkles :size="16" class="animate-pulse" />
            <span>프로필 기반 추천 찾는 중...</span>
          </div>
        </div>
        <div v-if="profileBasedRecommendations.length > 0" class="grid lg:grid-cols-2 gap-8">
          <router-link
            v-for="policy in profileBasedRecommendations"
            :key="policy.id"
            :to="`/policy/${policy.id}`"
            class="bg-white rounded-2xl shadow-md hover:shadow-xl transition-all p-8 border-2 border-transparent hover:border-blue-200 group"
          >
            <div class="flex items-start justify-between mb-4">
              <div class="flex items-center gap-3">
                <span class="px-4 py-1.5 bg-blue-100 text-blue-700 rounded-full">
                  {{ policy.category }}
                </span>
                <span class="text-gray-500">{{ policy.organization }}</span>
              </div>
              <span class="text-gray-500 bg-gray-50 px-3 py-1 rounded-full text-sm">{{ policy.region }}</span>
            </div>
            <h3 class="text-blue-900 mb-3 text-2xl group-hover:text-blue-700 transition-colors">{{ policy.title }}</h3>

            <div class="flex flex-wrap gap-2 text-xs text-gray-600 mb-3">
              <span class="px-2 py-1 rounded-full bg-gray-100">프로필 {{ formatScore(policy.profile_score_10) }}</span>
              <span
                v-if="policy.policy_target_required"
                :class="[
                  'px-2 py-1 rounded-full',
                  policy.policy_target_match ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
                ]"
              >
                정책 대상 {{ policy.policy_target_match ? '충족' : '미충족' }}
              </span>
            </div>

            <div class="flex flex-wrap gap-2">
              <span
                v-for="tag in policy.tags"
                :key="tag"
                class="px-3 py-1 bg-gray-100 text-gray-600 rounded-lg text-sm"
              >
                #{{ tag }}
              </span>
            </div>
          </router-link>
        </div>
        <div v-else class="bg-white rounded-2xl p-16 text-center shadow-md">
          <div class="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Search :size="40" class="text-gray-400" />
          </div>
          <p class="text-gray-500 text-lg mb-2">프로필에 맞는 정책을 찾지 못했어요.</p>
          <p class="text-gray-400">관심사나 지역을 바꿔 검색해 보세요.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRouter } from 'vue-router';
import { Sparkles, AlertCircle, Search, ArrowRight } from 'lucide-vue-next';
import { useUserStore } from '../stores/userStore';
import { usePolicyStore } from '../stores/policyStore';
import { useAuthStore } from '../stores/authStore';
import { request } from '../api/requestHelper'; // lightweight helper for direct API calls

const router = useRouter();
const authStore = useAuthStore();
const userStore = useUserStore();
const policyStore = usePolicyStore();

const isLoggedIn = computed(() => authStore.isAuthenticated);

const ragQuery = ref('');
const showRagResults = ref(false);
const ragBasedRecommendations = ref([]);
const recommendedFromApi = ref([]);
const top3Cards = ref([]);
const queryExamples = ref([]);
const profileLoading = ref(false);
const ragLoading = ref(false);

const loadRecommendations = async () => {
  profileLoading.value = true;
  if (!userStore.isProfileComplete) {
    recommendedFromApi.value = [];
    top3Cards.value = [];
    profileLoading.value = false;
    return;
  }
  // 기본 추천: backend /recommend/ (GET)
  const data = await request('/recommend/');
  recommendedFromApi.value = data?.results || [];
  // 기본 로드는 리스트만, Top3는 사용자 질의 이후 노출
  queryExamples.value = (data?.query_examples || []).slice(0, 2);
  profileLoading.value = false;
};

onMounted(async () => {
  if (!authStore.isAuthenticated) return;
  await userStore.loadProfile();
  policyStore.loadPolicies();
  loadRecommendations();
});

watch(
  () => ({ ...userStore.profile }),
  () => {
    loadRecommendations();
  },
  { deep: true }
);

const profileBasedRecommendations = computed(() => {
  return recommendedFromApi.value || [];
});

const formatScore = (val) => {
  if (val === null || val === undefined) return '—';
  const num = Number(val);
  if (!Number.isFinite(num)) return '—';
  return Number(num.toFixed(1));
};

const handleRagSearch = () => {
  const query = ragQuery.value.trim();
  if (!query) {
    ragBasedRecommendations.value = [];
    showRagResults.value = false;
    return;
  }
  (async () => {
    ragLoading.value = true;
    try {
      const data = await request('/recommend/detail/', {
        method: 'POST',
        body: JSON.stringify({ query }),
      });
      ragBasedRecommendations.value = data?.results || [];
      showRagResults.value = true;
      // RAG top3가 있으면 하이라이트 교체
      top3Cards.value = data?.top3?.length ? data.top3 : top3Cards.value;
      queryExamples.value = (data?.query_examples || []).slice(0, 2) || queryExamples.value;
    } finally {
      ragLoading.value = false;
    }
  })();
};

const goLogin = () => router.push('/login');
const goOnboarding = () => router.push('/onboarding');
</script>

<style scoped>
.loading-overlay {
  @apply fixed inset-0 bg-white/70 backdrop-blur-sm flex items-center justify-center z-50;
}
</style>
