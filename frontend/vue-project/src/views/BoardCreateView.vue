<template>
  <div class="max-w-[900px] mx-auto px-6 lg:px-10 py-12">
    <h1 class="text-3xl font-semibold text-blue-900 mb-6">게시글 작성</h1>

    <div class="bg-white rounded-2xl shadow-md border border-gray-100 p-8">
      <form class="space-y-6" @submit.prevent="handleSubmit">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">카테고리</label>
          <select v-model="form.category" class="w-full border rounded-lg px-4 py-3 focus:ring-2 focus:ring-blue-500">
            <option value="notice">공지사항</option>
            <option value="review">자료실</option>
            <option value="free">자유게시판</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">제목</label>
          <input
            v-model="form.title"
            type="text"
            required
            class="w-full border rounded-lg px-4 py-3 focus:ring-2 focus:ring-blue-500"
            placeholder="제목을 입력하세요"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">내용</label>
          <textarea
            v-model="form.content"
            rows="8"
            required
            class="w-full border rounded-lg px-4 py-3 focus:ring-2 focus:ring-blue-500 resize-none"
            placeholder="내용을 입력하세요"
          />
        </div>

        <div class="flex justify-end gap-3">
          <router-link
            to="/boards"
            class="px-5 py-3 rounded-lg border border-gray-200 text-gray-700 hover:bg-gray-50 transition"
          >
            취소
          </router-link>
          <button
            type="submit"
            class="px-6 py-3 rounded-lg bg-gradient-to-r from-blue-500 to-cyan-500 text-white shadow-md hover:shadow-lg transition"
            :disabled="boardStore.loading"
          >
            {{ boardStore.loading ? '저장 중...' : '작성하기' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue';
import { useRouter } from 'vue-router';
import { useBoardStore } from '../stores/boardStore';
import { useAuthStore } from '../stores/authStore';

const boardStore = useBoardStore();
const authStore = useAuthStore();
const router = useRouter();

const form = reactive({
  category: 'notice',
  title: '',
  content: '',
});

const handleSubmit = async () => {
  if (!authStore.isAuthenticated) {
    alert('로그인 후 작성할 수 있습니다.');
    router.push('/login');
    return;
  }
  try {
    const created = await boardStore.addBoard(form);
    router.push(`/boards/${created.id}`);
  } catch (err) {
    alert(err?.message || '작성에 실패했습니다.');
  }
};
</script>
