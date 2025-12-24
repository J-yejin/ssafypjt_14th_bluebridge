<template>
  <div class="max-w-[1240px] mx-auto px-4 lg:px-8 py-10 grid grid-cols-[1fr_280px] gap-6 items-start">
    <!-- 메인 리스트 -->
    <section class="bg-white rounded-2xl shadow-md border border-gray-100 p-6">
      <div class="flex items-center justify-between mb-8">
        <div>
          <h1 class="text-3xl font-semibold text-blue-900">정책 게시판</h1>
          <p class="text-gray-600 mt-2">카테고리를 선택해 정책 게시글 목록을 확인하세요.</p>
        </div>
        <router-link
          v-if="authStore.isAuthenticated"
          to="/boards/new"
          class="px-4 py-2.5 rounded-lg bg-gradient-to-r from-blue-500 to-cyan-500 text-white shadow-md hover:shadow-lg transition"
        >
          작성하기
        </router-link>
      </div>

      <div class="bg-white rounded-2xl shadow-inner border border-gray-100 overflow-hidden">
        <div class="overflow-x-auto">
          <div class="min-w-[720px]">
            <div v-if="boardStore.loading" class="p-8 text-center text-gray-500">불러오는 중...</div>
            <div v-else-if="boardStore.error" class="p-8 text-center text-red-500">{{ boardStore.error }}</div>
            <div v-else-if="filteredBoards.length === 0" class="p-8 text-center text-gray-500">게시글이 없습니다.</div>
            <ul v-else>
              <li
                v-for="board in filteredBoards"
                :key="board.id"
                class="grid grid-cols-[80px_1fr_160px_140px] items-center px-6 py-4 border-t border-gray-100 hover:bg-blue-50 transition cursor-pointer text-sm"
                @click="handleSelect(board.id)"
              >
                <span class="text-gray-500">작성 번호 : {{ board.id }}</span>
                <div class="flex flex-col">
                  <span class="text-base text-blue-900">제목 : {{ board.title }}</span>
                  <span class="text-xs text-gray-500">카테고리 : {{ displayCategory(board.category) }}</span>
                </div>
                <span class="text-gray-600">작성자 : {{ board.user || '익명' }}</span>
                <span class="text-right text-gray-500">작성 일시 : {{ formatDate(board.created_at) }}</span>
              </li>
            </ul>
          </div>
        </div>
      </div>
    </section>

    <!-- 사이드바 -->
    <aside class="bg-white rounded-2xl shadow-md border border-gray-100 p-4 lg:order-last">
      <div class="rounded-2xl bg-gradient-to-b from-blue-500 to-cyan-500 text-white p-5 mb-4">
        <p class="text-sm opacity-80">정책 게시판</p>
        <h2 class="text-2xl font-bold mt-1">카테고리</h2>
      </div>
      <div class="space-y-2">
        <button
          v-for="item in categories"
          :key="item.value"
          @click="setCategory(item.value)"
          :class="[
            'w-full text-left px-4 py-3 rounded-xl border transition flex items-center justify-between',
            selectedCategory === item.value
              ? 'border-blue-500 bg-blue-50 text-blue-700 font-semibold'
              : 'border-gray-200 bg-white text-gray-700 hover:bg-gray-50'
          ]"
        >
          <span>{{ item.label }}</span>
          <span v-if="selectedCategory === item.value" class="text-blue-500 text-sm">선택됨</span>
        </button>
      </div>
    </aside>
  </div>
</template>

<script setup>
import { computed, onMounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useBoardStore } from '../stores/boardStore';
import { useAuthStore } from '../stores/authStore';

const boardStore = useBoardStore();
const authStore = useAuthStore();
const route = useRoute();
const router = useRouter();

const selectedCategory = ref('all');

const categories = [
  { label: '전체', value: 'all' },
  { label: '공지사항', value: 'notice' },
  { label: '자료실', value: 'review' },
  { label: '자유게시판', value: 'free' },
];

const formatDate = (value) => {
  if (!value) return '';
  return new Date(value).toLocaleDateString();
};

const displayCategory = (value) => {
  const map = {
    notice: '공지사항',
    review: '자료실',
    free: '자유게시판',
    question: '자유게시판',
  };
  return map[value] || '기타';
};

const filteredBoards = computed(() => {
  let list = [...(boardStore.boards || [])];
  if (selectedCategory.value !== 'all') {
    const group = {
      notice: ['notice'],
      review: ['review'],
      free: ['free', 'question'],
    }[selectedCategory.value] || [];
    list = list.filter((b) => group.some((g) => (b.category || '').toLowerCase().includes(g)));
  }
  return list;
});

const handleSelect = (id) => {
  if (!authStore.isAuthenticated) {
    alert('로그인 후 게시글을 확인할 수 있습니다.');
    router.push('/login');
    return;
  }
  router.push(`/boards/${id}`);
};

const setCategory = (value) => {
  selectedCategory.value = value;
  router.replace({ query: { ...route.query, category: value === 'all' ? undefined : value } });
};

const syncCategoryFromRoute = () => {
  const q = route.query.category;
  if (q && categories.some((c) => c.value === q)) {
    selectedCategory.value = q;
  } else {
    selectedCategory.value = 'all';
  }
};

onMounted(() => {
  boardStore.loadBoards();
  syncCategoryFromRoute();
});

watch(
  () => route.query.category,
  () => syncCategoryFromRoute()
);
</script>
