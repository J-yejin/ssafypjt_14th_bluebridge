<template>
  <div class="min-h-screen">
    <div class="max-w-[1400px] mx-auto px-8 lg:px-12 py-12">
      <div class="mb-12">
        <h1 class="text-blue-900 mb-3 text-4xl">정책 검색</h1>
        <p class="text-gray-600 text-lg">원하는 조건으로 청년 정책을 탐색하세요.</p>
      </div>

      <!-- 검색 -->
      <div class="mb-8 bg-white rounded-2xl shadow-lg p-8 border border-blue-100">
        <div class="flex gap-6">
          <div class="flex-1 relative">
            <Search class="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 w-6 h-6" />
            <input
              type="text"
              placeholder="정책명이나 키워드를 입력하세요"
              v-model="searchTerm"
              class="w-full pl-14 pr-12 py-4 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
            />
            <button
              v-if="searchTerm"
              @click="searchTerm = ''"
              class="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600"
            >
              <X class="w-6 h-6" />
            </button>
          </div>
          <button
            @click="showFilters = !showFilters"
            :class="[
              'flex items-center gap-3 px-8 py-4 rounded-xl transition-all text-lg',
              showFilters ? 'bg-blue-600 text-white shadow-lg' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
            ]"
          >
            <Filter :size="20" />
            <span>필터</span>
          </button>
        </div>

        <!-- 필터 -->
        <div v-if="showFilters" class="mt-8 pt-8 border-t-2 border-gray-100 grid lg:grid-cols-3 gap-6">
          <div>
            <label class="block text-gray-700 mb-3 text-lg">카테고리</label>
            <select
              v-model="selectedCategory"
              class="w-full px-5 py-3.5 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
            >
              <option v-for="cat in categories" :key="cat.value" :value="cat.value">
                {{ cat.label }}
              </option>
            </select>
          </div>

          <div>
            <label class="block text-gray-700 mb-3 text-lg">지역</label>
            <select
              v-model="selectedRegion"
              class="w-full px-5 py-3.5 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
            >
              <option v-for="region in regions" :key="region.value" :value="region.value">
                {{ region.label }}
              </option>
            </select>
          </div>

          <div>
            <label class="block text-gray-700 mb-3 text-lg">정렬</label>
            <select
              v-model="sortBy"
              class="w-full px-5 py-3.5 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
            >
              <option value="title">제목순</option>
              <option value="category">카테고리순</option>
            </select>
          </div>
        </div>
      </div>

      <!-- 결과 상단 -->
      <div class="mb-6 flex items-center justify-between">
        <p class="text-gray-600 text-lg">
          총 <span class="text-blue-600">{{ filteredAndSortedPolicies.length }}</span>개의 정책
        </p>
        <button
          v-if="searchTerm || selectedCategory || selectedRegion"
          @click="resetFilters"
          class="text-blue-600 hover:text-blue-700 flex items-center gap-2 px-4 py-2 hover:bg-blue-50 rounded-lg transition-all"
        >
          <X :size="20" />
          <span>필터 초기화</span>
        </button>
      </div>

      <!-- 목록 -->
      <div class="grid lg:grid-cols-2 gap-8">
        <router-link
          v-for="policy in filteredAndSortedPolicies"
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
              v-for="tag in policy.tags.slice(0, 4)"
              :key="tag"
              class="px-3 py-1 bg-gray-100 text-gray-600 rounded-lg text-sm"
            >
              #{{ tag }}
            </span>
          </div>
        </router-link>

        <div v-if="!policyStore.loading && filteredAndSortedPolicies.length === 0" class="col-span-2 text-center py-20 bg-white rounded-2xl shadow-md">
          <div class="w-20 h-20 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Search :size="40" class="text-gray-400" />
          </div>
          <p class="text-gray-500 text-lg">조건에 맞는 정책을 찾지 못했습니다.</p>
          <p class="text-gray-400 mt-2">검색어나 필터를 조정해보세요.</p>
        </div>

        <div v-if="policyStore.loading" class="col-span-2 text-center py-16 text-gray-500">
          정책을 불러오는 중입니다...
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { Search, Filter, X } from 'lucide-vue-next';
import { usePolicyStore } from '../stores/policyStore';

const policyStore = usePolicyStore();
const searchTerm = ref('');
const selectedCategory = ref('');
const selectedRegion = ref('');
const sortBy = ref('title');
const showFilters = ref(false);

const categories = [
  { label: '전체', value: '' },
  { label: '일자리', value: '일자리' },
  { label: '교육', value: '교육' },
  { label: '복지문화', value: '복지문화' },
  { label: '건강', value: '건강' },
  { label: '생활지원', value: '생활지원' },
  { label: '재무/법률', value: '재무/법률' },
  { label: '위기·안전', value: '위기·안전' },
  { label: '가족/권리', value: '가족/권리' },
  { label: '기타', value: '기타' },
];

const regions = [
  { label: '전체', value: '' },
  { label: '전국', value: '전국' },
  { label: '서울특별시', value: '서울특별시' },
  { label: '부산광역시', value: '부산광역시' },
  { label: '대구광역시', value: '대구광역시' },
  { label: '인천광역시', value: '인천광역시' },
  { label: '광주광역시', value: '광주광역시' },
  { label: '대전광역시', value: '대전광역시' },
  { label: '울산광역시', value: '울산광역시' },
  { label: '세종특별자치시', value: '세종특별자치시' },
  { label: '경기도', value: '경기도' },
  { label: '강원특별자치도', value: '강원특별자치도' },
  { label: '충청북도', value: '충청북도' },
  { label: '충청남도', value: '충청남도' },
  { label: '전라북도', value: '전라북도' },
  { label: '전라남도', value: '전라남도' },
  { label: '경상북도', value: '경상북도' },
  { label: '경상남도', value: '경상남도' },
  { label: '제주특별자치도', value: '제주특별자치도' },
  { label: '기타', value: '기타' },
];

onMounted(() => {
  policyStore.loadPolicies();
});

const filteredAndSortedPolicies = computed(() => {
  const list = policyStore.policies || [];
  let filtered = list.filter((policy) => {
    const term = searchTerm.value.trim().toLowerCase();
    const matchesSearch =
      term === '' ||
      policy.title.toLowerCase().includes(term) ||
      policy.description.toLowerCase().includes(term) ||
      policy.tags.some((tag) => tag.toLowerCase().includes(term));

    const matchesCategory = selectedCategory.value === '' || policy.category === selectedCategory.value;
    const matchesRegion =
      selectedRegion.value === '' ||
      (policy.regionBuckets || [policy.regionBucket]).includes(selectedRegion.value);

    return matchesSearch && matchesCategory && matchesRegion;
  });

  filtered.sort((a, b) => {
    if (sortBy.value === 'title') return a.title.localeCompare(b.title);
    if (sortBy.value === 'category') return a.category.localeCompare(b.category);
    return 0;
  });

  return filtered;
});

const resetFilters = () => {
  searchTerm.value = '';
  selectedCategory.value = '';
  selectedRegion.value = '';
};
</script>
