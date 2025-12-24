<template>
  <div class="max-w-[900px] mx-auto px-6 lg:px-10 py-12">
    <div v-if="boardStore.loading" class="text-center text-gray-500">불러오는 중...</div>
    <div v-else-if="boardStore.error" class="text-center text-red-500">{{ boardStore.error }}</div>
    <div v-else-if="!boardStore.current" class="text-center text-gray-500">게시글이 없습니다.</div>
    <div v-else class="bg-white rounded-2xl shadow-md border border-gray-100 p-8 space-y-8">
      <div class="flex justify-between items-start mb-6">
        <div>
          <p class="text-sm text-gray-500">{{ displayCategory(boardStore.current.category) }}</p>
          <h1 class="text-3xl font-semibold text-blue-900 mt-2">{{ boardStore.current.title }}</h1>
          <p class="text-sm text-gray-500 mt-2">
            작성자 {{ boardStore.current.user }} · 조회 {{ boardStore.current.views }} ·
            {{ formatDate(boardStore.current.created_at) }}
          </p>
        </div>
      </div>
      <div class="prose max-w-none text-gray-700 whitespace-pre-line leading-relaxed">
        {{ boardStore.current.content }}
      </div>

      <!-- 댓글 -->
      <div class="pt-6 border-t border-gray-100">
        <h2 class="text-xl font-semibold text-blue-900 mb-4">댓글</h2>
        <div v-if="sortedComments.length === 0" class="text-gray-500 mb-4">첫 댓글을 남겨주세요.</div>
        <ul class="space-y-4">
          <li
            v-for="comment in sortedComments"
            :key="comment.id"
            class="border border-gray-100 rounded-xl p-4 bg-gray-50"
          >
            <div class="flex justify-between items-center text-sm text-gray-500 mb-2">
              <span>{{ comment.user }}</span>
              <div class="flex items-center gap-3">
                <span>{{ formatDate(comment.created_at) }}</span>
                <button
                  v-if="comment.user === authStore.username"
                  type="button"
                  class="text-red-500 hover:underline"
                  @click="handleDeleteComment(comment.id)"
                >
                  삭제
                </button>
              </div>
            </div>
            <p class="text-gray-800 whitespace-pre-line">{{ comment.content }}</p>
          </li>
        </ul>

        <div class="mt-6">
          <div v-if="authStore.isAuthenticated" class="space-y-3">
            <textarea
              v-model="newComment"
              rows="3"
              class="w-full border rounded-lg px-4 py-3 focus:ring-2 focus:ring-blue-500 resize-none"
              placeholder="댓글을 입력하세요"
            />
            <div class="flex justify-end">
              <button
                type="button"
                @click="handleAddComment"
                class="px-5 py-2.5 rounded-lg bg-gradient-to-r from-blue-500 to-cyan-500 text-white shadow-md hover:shadow-lg transition"
              >
                댓글 등록
              </button>
            </div>
          </div>
          <div v-else class="text-gray-500">
            댓글을 작성하려면
            <router-link to="/login" class="text-blue-600 underline">로그인</router-link> 해주세요.
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useBoardStore } from '../stores/boardStore';
import { useAuthStore } from '../stores/authStore';

const route = useRoute();
const router = useRouter();
const boardStore = useBoardStore();
const authStore = useAuthStore();
const newComment = ref('');

const formatDate = (value) => {
  if (!value) return '';
  return new Date(value).toLocaleString();
};

const displayCategory = (value) => {
  const map = {
    notice: '공지사항',
    resource: '자료실',
    review: '자료실',
    free: '자유게시판',
    question: '자유게시판',
  };
  return map[value] || '기타';
};

const sortedComments = computed(() => {
  const list = boardStore.current?.comments || [];
  return [...list].sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
});

const load = async () => {
  if (!authStore.isAuthenticated) {
    alert('로그인 후 게시글을 확인할 수 있습니다.');
    router.push('/login');
    return;
  }
  try {
    await boardStore.loadBoardById(route.params.id);
  } catch (err) {
    if (String(err?.message || '').toLowerCase().includes('authentication')) {
      alert('로그인이 필요합니다.');
      router.push('/login');
    }
  }
};

const handleAddComment = async () => {
  const content = newComment.value.trim();
  if (!content) return;
  try {
    await boardStore.addComment(boardStore.current.id, { content });
    newComment.value = '';
  } catch (err) {
    alert(err?.message || '댓글 등록에 실패했습니다.');
  }
};

const handleDeleteComment = async (commentId) => {
  try {
    await boardStore.removeComment(commentId);
  } catch (err) {
    alert(err?.message || '댓글 삭제에 실패했습니다.');
  }
};

onMounted(load);
</script>
