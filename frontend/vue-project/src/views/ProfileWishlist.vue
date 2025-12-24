<template>
  <div class="min-h-screen">
    <div v-if="!isLoggedIn" class="min-h-screen flex items-center justify-center">
      <div class="max-w-2xl mx-auto px-8 lg:px-12">
        <div class="bg-white rounded-3xl shadow-2xl p-12 text-center">
          <div class="w-24 h-24 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6 shadow-lg">
            <AlertCircle :size="48" class="text-blue-600" />
          </div>
          <h2 class="text-blue-900 mb-4 text-3xl">로그인이 필요해요</h2>
          <p class="text-gray-600 mb-8 text-lg leading-relaxed">
            관심정책을 보려면 로그인 후 이용해주세요.
          </p>
          <router-link
            to="/login"
            class="inline-flex items-center gap-3 bg-gradient-to-r from-blue-500 to-cyan-500 text-white px-10 py-4 rounded-2xl hover:shadow-2xl transition-all text-lg shadow-lg"
          >
            로그인하러 가기
          </router-link>
        </div>
      </div>
    </div>
    <div v-else class="max-w-[1200px] mx-auto px-8 lg:px-12 py-12">
      <div class="mb-12">
        <h1 class="text-blue-900 mb-3 text-4xl">나의 관심정책</h1>
        <p class="text-gray-600 text-lg">위시리스트에 저장한 정책을 모아봤어요.</p>
      </div>

      <div v-if="loading" class="text-gray-500 text-lg">불러오는 중입니다...</div>
      <div v-else-if="error" class="bg-red-50 border border-red-200 text-red-700 rounded-2xl p-6">
        {{ error }}
      </div>

      <div v-else class="grid lg:grid-cols-2 gap-8">
        <router-link
          v-for="item in wishlist"
          :key="item.id"
          :to="`/policy/${item.policy.id}`"
          class="bg-white rounded-2xl shadow-md hover:shadow-xl transition-all p-8 border-2 border-transparent hover:border-blue-200 group"
        >
          <div class="flex items-center justify-between mb-4">
            <span class="px-4 py-1.5 bg-blue-100 text-blue-700 rounded-full">관심 정책</span>
            <span class="text-gray-500 text-sm">{{ formatRegion(item.policy) }}</span>
          </div>
          <h3 class="text-blue-900 mb-3 text-2xl group-hover:text-blue-700 transition-colors">
            {{ item.policy.title }}
          </h3>
          <p class="text-gray-600 line-clamp-3">
            {{ item.policy.summary || '요약 정보가 없습니다.' }}
          </p>
        </router-link>

        <div v-if="wishlist.length === 0" class="col-span-2 text-center py-16 bg-white rounded-2xl shadow-md">
          <p class="text-gray-500 text-lg">아직 관심정책이 없습니다.</p>
          <p class="text-gray-400 mt-2">정책 상세 페이지에서 관심 정책으로 저장해보세요.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { AlertCircle } from 'lucide-vue-next';
import { fetchWishlist } from '../api/client';
import { useAuthStore } from '../stores/authStore';

const wishlist = ref([]);
const loading = ref(false);
const error = ref('');
const authStore = useAuthStore();
const isLoggedIn = computed(() => authStore.isAuthenticated);

const formatRegion = (policy) => {
  const region = policy.region_sigungu || policy.region_sido || '전국';
  return region || '전국';
};

const loadWishlist = async () => {
  loading.value = true;
  error.value = '';
  try {
    const data = await fetchWishlist();
    wishlist.value = Array.isArray(data) ? data : [];
  } catch (err) {
    error.value = err.message || '관심정책을 불러오지 못했습니다.';
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  if (!isLoggedIn.value) return;
  loadWishlist();
});
</script>

