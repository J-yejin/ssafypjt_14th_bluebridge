import { defineStore } from 'pinia';
import { ref } from 'vue';
import { fetchBoards, fetchBoardById, createBoard, createComment, deleteComment } from '../api/client';

export const useBoardStore = defineStore('board', () => {
  const boards = ref([]);
  const current = ref(null);
  const loading = ref(false);
  const error = ref(null);

  const loadBoards = async () => {
    loading.value = true;
    error.value = null;
    try {
      const data = await fetchBoards();
      boards.value = data?.results || data || [];
    } catch (err) {
      error.value = err.message || '게시글을 불러오지 못했습니다.';
    } finally {
      loading.value = false;
    }
  };

  const loadBoardById = async (id) => {
    loading.value = true;
    error.value = null;
    try {
      const data = await fetchBoardById(id);
      current.value = data;
      return data;
    } catch (err) {
      error.value = err.message || '게시글을 불러오지 못했습니다.';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const addBoard = async (payload) => {
    loading.value = true;
    error.value = null;
    try {
      const data = await createBoard(payload);
      // 목록 최신화
      boards.value = [data, ...boards.value];
      return data;
    } catch (err) {
      error.value = err.message || '게시글을 작성하지 못했습니다.';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const addComment = async (boardId, payload) => {
    loading.value = true;
    error.value = null;
    try {
      const data = await createComment(boardId, payload);
      if (current.value?.id === boardId) {
        current.value.comments = [...(current.value.comments || []), data];
      }
      return data;
    } catch (err) {
      error.value = err.message || '댓글을 작성하지 못했습니다.';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const removeComment = async (commentId) => {
    loading.value = true;
    error.value = null;
    try {
      await deleteComment(commentId);
      if (current.value?.comments) {
        current.value.comments = current.value.comments.filter((c) => c.id !== commentId);
      }
    } catch (err) {
      error.value = err.message || '댓글을 삭제하지 못했습니다.';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  return {
    boards,
    current,
    loading,
    error,
    loadBoards,
    loadBoardById,
    addBoard,
    addComment,
    removeComment,
  };
});
