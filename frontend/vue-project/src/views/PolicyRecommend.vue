<template>
  <div class="min-h-screen">
    <div v-if="!userStore.isProfileComplete" class="min-h-screen flex items-center justify-center">
      <div class="max-w-2xl mx-auto px-8 lg:px-12">
        <div class="bg-white rounded-3xl shadow-2xl p-12 text-center">
          <div class="w-24 h-24 bg-yellow-100 rounded-full flex items-center justify-center mx-auto mb-6 shadow-lg">
            <AlertCircle :size="48" class="text-yellow-600" />
          </div>
          <h2 class="text-blue-900 mb-4 text-3xl">프로필을 완성해주세요</h2>
          <p class="text-gray-600 mb-8 text-lg leading-relaxed">
            맞춤 추천을 받으려면 기본 프로필 정보를 먼저 입력해주세요.
            <br />
            간단한 정보만으로 AI 추천을 바로 확인할 수 있습니다.
          </p>
          <router-link
            to="/profile"
            class="inline-flex items-center gap-3 bg-gradient-to-r from-blue-500 to-cyan-500 text-white px-10 py-4 rounded-2xl hover:shadow-2xl transition-all text-lg shadow-lg"
          >
            <span>프로필 작성하러 가기</span>
            <ArrowRight :size="24" />
          </router-link>
        </div>
      </div>
    </div>

    <div v-else class="max-w-[1400px] mx-auto px-8 lg:px-12 py-12">
      <div class="mb-12">
        <h1 class="text-blue-900 mb-3 text-4xl">정책 추천</h1>
        <p class="text-gray-600 text-lg">
          <span class="text-blue-600">{{ userStore.profile.name }}</span>님의 프로필을 기반으로 맞춤 정책을 추천합니다.
        </p>
      </div>

      <!-- RAG Search -->
      <div class="bg-white rounded-2xl shadow-xl p-10 mb-12 border border-blue-100">
        <div class="flex items-start gap-4 mb-6">
          <div class="w-12 h-12 bg-gradient-to-br from-cyan-400 to-cyan-600 rounded-xl flex items-center justify-center flex-shrink-0 shadow-md">
            <Sparkles :size="24" class="text-white" />
          </div>
          <div>
            <h2 class="text-blue-900 mb-2 text-2xl">AI 정책 검색</h2>
            <p class="text-gray-600 text-lg">
              궁금한 정책을 자연어로 입력하면 AI가 관련 정책을 찾아드립니다.
            </p>
          </div>
        </div>
        <div class="flex gap-6">
          <input
            type="text"
            placeholder="예) 창업 자금 지원 받고 싶어요, 전월세 대출 알아보고 싶어요"
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
              <p class="text-gray-600 mb-5 line-clamp-2 leading-relaxed">{{ policy.description }}</p>
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
        <h2 class="text-blue-900 mb-6 text-3xl">프로필 기반 추천</h2>
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
            <p class="text-gray-600 mb-5 line-clamp-2 leading-relaxed">{{ policy.description }}</p>
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
          <p class="text-gray-500 text-lg mb-2">아직 프로필에 맞는 정책을 찾지 못했습니다.</p>
          <p class="text-gray-400">키워드 검색을 활용하거나 관심사를 더 추가해보세요.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { Sparkles, AlertCircle, Search, ArrowRight } from 'lucide-vue-next';
import { useUserStore } from '../stores/userStore';
import { usePolicyStore } from '../stores/policyStore';

const userStore = useUserStore();
const policyStore = usePolicyStore();

const ragQuery = ref('');
const showRagResults = ref(false);
const ragBasedRecommendations = ref([]);
const recommendedFromApi = ref([]);

const employmentMap = {
  '취업': 'employed',
  '미취업': 'unemployed',
  '학생': 'student',
  '자영업': 'self-employed',
};

const loadRecommendations = async () => {
  if (!userStore.isProfileComplete) {
    recommendedFromApi.value = [];
    return;
  }
  const results = await policyStore.recommendPolicies(userStore.profile);
  recommendedFromApi.value = results || [];
};

onMounted(() => {
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
  if (recommendedFromApi.value.length) return recommendedFromApi.value;
  const list = policyStore.policies || [];
  return list.filter((policy) => {
    const [minAge, maxAge] = policy.ageRange.split('-').map(Number);
    const userAge = parseInt(userStore.profile.age, 10);
    const ageMatch = !Number.isNaN(userAge) ? userAge >= minAge && userAge <= maxAge : true;

    const employmentKey = employmentMap[userStore.profile.employmentStatus] || '';
    const employmentMatch = employmentKey ? policy.employmentStatus.includes(employmentKey) : true;

    const interests = userStore.profile.interests.map((i) => i.toLowerCase());
    const interestMatch = interests.length
      ? policy.tags.some((tag) => interests.includes(tag.toLowerCase())) || interests.includes(policy.category.toLowerCase())
      : true;

    return ageMatch && employmentMatch && interestMatch;
  });
});

const handleRagSearch = () => {
  const query = ragQuery.value.trim();
  if (!query) {
    ragBasedRecommendations.value = [];
    showRagResults.value = false;
    return;
  }
  ragBasedRecommendations.value = policyStore.searchPolicies(query);
  showRagResults.value = true;
};
</script>
