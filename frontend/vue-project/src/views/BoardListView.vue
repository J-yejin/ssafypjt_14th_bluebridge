<template>
  <div class="max-w-[1200px] mx-auto px-6 lg:px-10 py-12">
    <div class="flex items-center justify-between mb-8">
      <div>
        <h1 class="text-3xl font-semibold text-blue-900">게시글</h1>
        <p class="text-gray-600 mt-2">전체 게시글 제목 목록을 보여줍니다.</p>
      </div>
      <router-link
        v-if="authStore.isAuthenticated"
        to="/boards/new"
        class="px-4 py-2.5 rounded-lg bg-gradient-to-r from-blue-500 to-cyan-500 text-white shadow-md hover:shadow-lg transition"
      >
        글쓰기
      </router-link>
    </div>

    <div class="bg-white rounded-2xl shadow-md border border-gray-100">
      <div v-if="boardStore.loading" class="p-8 text-center text-gray-500">불러오는 중...</div>
      <div v-else-if="boardStore.error" class="p-8 text-center text-red-500">{{ boardStore.error }}</div>
      <ul v-else>
        <li
          v-for="board in boardStore.boards"
          :key="board.id"
          class="flex items-center justify-between px-6 py-4 border-b border-gray-100 last:border-b-0 hover:bg-gray-50 transition cursor-pointer"
          @click="handleSelect(board.id)"
        >
          <div class="flex flex-col">
            <span class="text-lg text-blue-900">{{ board.title }}</span>
            <span class="text-xs text-gray-500">작성자 {{ board.user }} · 조회 {{ board.views }}</span>
          </div>
          <span class="text-sm text-gray-400">{{ formatDate(board.created_at) }}</span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useBoardStore } from '../stores/boardStore';
import { useAuthStore } from '../stores/authStore';

const boardStore = useBoardStore();
const authStore = useAuthStore();
const router = useRouter();

const formatDate = (value) => {
  if (!value) return '';
  return new Date(value).toLocaleDateString();
};

const handleSelect = (id) => {
  if (!authStore.isAuthenticated) {
    alert('로그인 후 게시글을 확인할 수 있습니다.');
    router.push('/login');
    return;
  }
  router.push(`/boards/${id}`);
};

onMounted(() => {
  boardStore.loadBoards();
});
</script>
