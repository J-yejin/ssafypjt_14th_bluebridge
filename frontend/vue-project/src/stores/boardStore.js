import { defineStore } from 'pinia';
import { ref } from 'vue';
import {
  fetchBoards,
  fetchBoardById,
  createBoard,
  createComment,
  deleteComment,
  fetchMyComments,
  toggleBoardLike,
  updateBoard,
  deleteBoard,
} from '../api/client';

export const useBoardStore = defineStore('board', () => {
  const boards = ref([]);
  const current = ref(null);
  const myComments = ref([]);
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
      boards.value = [data, ...boards.value];
      return data;
    } catch (err) {
      error.value = err.message || '게시글 등록에 실패했습니다.';
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
      error.value = err.message || '댓글 등록에 실패했습니다.';
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
      error.value = err.message || '댓글 삭제에 실패했습니다.';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const loadMyComments = async () => {
    loading.value = true;
    error.value = null;
    try {
      const data = await fetchMyComments();
      myComments.value = data || [];
    } catch (err) {
      error.value = err.message || '?ì¸? ??ê¸€ ???ë€?œ ì½ê¸°???¤íŒ¨?ˆìŠµ?ˆë‹¤.';
    } finally {
      loading.value = false;
    }
  };

  const editBoard = async (id, payload) => {
    loading.value = true;
    error.value = null;
    try {
      const data = await updateBoard(id, payload);
      if (current.value?.id === id) {
        current.value = { ...current.value, ...data };
      }
      boards.value = boards.value.map((b) => (b.id === id ? { ...b, ...data } : b));
      return data;
    } catch (err) {
      error.value = err.message || '게시글 수정에 실패했습니다.';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  const removeBoard = async (id) => {
    loading.value = true;
    error.value = null;
    try {
      await deleteBoard(id);
      boards.value = boards.value.filter((b) => b.id !== id);
      if (current.value?.id === id) current.value = null;
    } catch (err) {
      error.value = err.message || '게시글 삭제에 실패했습니다.';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  // alias to avoid stale HMR instances missing the action
  const deleteBoardAction = removeBoard;

  const toggleLike = async (boardId) => {
    loading.value = true;
    error.value = null;
    try {
      const data = await toggleBoardLike(boardId);
      if (current.value?.id === boardId) {
        current.value = {
          ...current.value,
          is_liked: data?.liked ?? current.value?.is_liked,
          like_count: data?.like_count ?? current.value?.like_count,
        };
      }
      boards.value = boards.value.map((b) =>
        b.id === boardId
          ? {
              ...b,
              is_liked: data?.liked ?? b.is_liked,
              like_count: data?.like_count ?? b.like_count,
            }
          : b
      );
      return data;
    } catch (err) {
      error.value = err.message || '좋아요 처리에 실패했습니다.';
      throw err;
    } finally {
      loading.value = false;
    }
  };

  return {
    boards,
    current,
    myComments,
    loading,
    error,
    loadBoards,
    loadBoardById,
    loadMyComments,
    addBoard,
    editBoard,
    removeBoard,
    deleteBoardAction,
    addComment,
    removeComment,
    toggleLike,
  };
});
