<template>
  <div class="board-page">
    <div class="container">
      <!-- 사이드바 -->
      <aside class="sidebar">
        <div class="sidebar-header">
          <p class="eyebrow">정책 게시판</p>
          <h2>카테고리</h2>
        </div>
        <div class="sidebar-menu">
          <button
            v-for="item in categories"
            :key="item.value"
            class="sidebar-item"
            :class="{ active: selectedCategory === item.value }"
            @click="setCategory(item.value)"
          >
            <span>{{ item.label }}</span>
          </button>
        </div>
      </aside>

      <!-- 메인 영역 -->
      <main class="content">
        <div class="content-header">
          <div>
            <h1>정책 게시판</h1>
            <p>총 게시물: {{ filteredBoards.length }}건</p>
          </div>
          <div class="actions">
            <select v-model="sortKey" class="sort-select">
              <option v-for="option in sortOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
            <input
              v-model="searchTerm"
              type="text"
              class="search-input"
              placeholder="검색어를 입력하세요"
            />
            <router-link v-if="authStore.isAuthenticated" to="/boards/new" class="write-btn">
              글 작성
            </router-link>
          </div>
        </div>

        <div class="table-wrapper">
          <div class="table-header">
            <span class="col-number">번호</span>
            <span class="col-title">제목</span>
            <span class="col-author">작성자</span>
            <span class="col-date">작성일</span>
          </div>
          <div v-if="boardStore.loading" class="empty">불러오는 중...</div>
          <div v-else-if="boardStore.error" class="empty error">{{ boardStore.error }}</div>
          <div v-else-if="filteredBoards.length === 0" class="empty">게시글이 없습니다.</div>
          <ul v-else class="table-rows">
            <li
              v-for="board in filteredBoards"
              :key="board.id"
              class="table-row"
              @click="handleSelect(board.id)"
            >
              <span class="col-number">{{ displayNumber(board) }}</span>
              <div class="col-title">
                <span class="title-text">{{ board.title }}</span>
              </div>
              <span class="col-author">{{ board.user || '익명' }}</span>
              <span class="col-date">{{ formatDate(board.created_at) }}</span>
            </li>
          </ul>
        </div>
      </main>
    </div>
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
const searchTerm = ref('');
const sortKey = ref('latest');

const sortOptions = [
  { value: 'latest', label: '\uCD5C\uC2E0\uC21C' },
  { value: 'likes', label: '\uC88B\uC544\uC694\uC21C' },
]; 

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
  if (searchTerm.value.trim()) {
    const q = searchTerm.value.toLowerCase();
    list = list.filter(
      (b) =>
        (b.title || '').toLowerCase().includes(q) ||
        (b.content || '').toLowerCase().includes(q) ||
        (b.user || '').toLowerCase().includes(q)
    );
  }
  const compareByDate = (a, b) => new Date(b.created_at) - new Date(a.created_at);
  const likeCount = (item) => item?.likes ?? item?.like_count ?? 0;
  const compareBySortKey =
    sortKey.value === "likes"
      ? (a, b) => likeCount(b) - likeCount(a) || compareByDate(a, b)
      : compareByDate;
  const categoryPriority = (item) => {
    const category = (item.category || '').toLowerCase();
    if (category === 'notice') return 0;
    if (category === 'review') return 1;
    return 2;
  };
  if (selectedCategory.value === 'all') {
    list = [...list].sort(
      (a, b) => categoryPriority(a) - categoryPriority(b) || compareBySortKey(a, b)
    );
  } else {
    list = [...list].sort(compareBySortKey);
  }
  return list;
});


const freeNumberMap = computed(() => {
  let count = 0;
  const map = new Map();
  filteredBoards.value.forEach((board) => {
    const category = (board.category || '').toLowerCase();
    if (category === 'free' || category === 'question') {
      count += 1;
      map.set(board.id, count);
    }
  });
  return map;
});

const displayNumber = (board) => {
  const category = (board.category || '').toLowerCase();
  if (category === 'notice') return '\uACF5\uC9C0';
  if (category === 'review') return '\uC790\uB8CC\uC2E4';
  return freeNumberMap.value.get(board.id) || '-';
};

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

<style scoped>
.board-page {
  background: #f7f8fb;
  min-height: 100vh;
  padding-top: 12px;
}

.container {
  display: grid;
  grid-template-columns: 1fr;
  gap: 20px;
}

@media (min-width: 1024px) {
  .container {
    grid-template-columns: minmax(220px, 20%) 1fr;
    align-items: start;
  }
}


.sidebar {
  background: #fff;
  border-radius: 18px;
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.06);
  border: 1px solid #e5e7eb;
  padding: 0;
  overflow: hidden;

  /* 핵심 */
  height: fit-content;   /* 콘텐츠만큼만 */
  position: sticky;
  top: 24px;             /* 스크롤 시 따라오기 시작 위치 */
}


.sidebar-header {
  background: linear-gradient(135deg, #4fb184 0%, #43a5d4 100%);
  color: #fff;
  padding: 18px 16px 14px 16px;
}

.sidebar-header .eyebrow {
  font-size: 12px;
  opacity: 0.85;
  margin: 0 0 4px 0;
}

.sidebar-header h2 {
  margin: 0;
  font-size: 22px;
  font-weight: 800;
}

.sidebar-menu {
  padding: 12px;
  display: grid;
  gap: 10px;
}

.sidebar-item {
  width: 100%;
  text-align: left;
  padding: 14px 14px;
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  background: #fff;
  color: #374151;
  font-weight: 600;
  transition: all 0.15s ease;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.sidebar-item:hover {
  background: #e7f5ec;
  border-color: #b7e0c8;
  color: #2f855a;
}

.sidebar-item.active {
  border: 1px solid #4fb184;
  background: #e1f4ea;
  color: #2f855a;
}

.content {
  background: #fff;
  border-radius: 18px;
  box-shadow: 0 12px 28px rgba(0, 0, 0, 0.06);
  border: 1px solid #e5e7eb;
  padding: 22px;
}

.content-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 12px;
  flex-wrap: wrap;
}

.content-header h1 {
  margin: 0;
  font-size: 26px;
  font-weight: 800;
}

.content-header p {
  margin: 4px 0 0 0;
  color: #6b7280;
}

.actions {
  display: flex;
  gap: 8px;
  align-items: center;
  flex-wrap: wrap;
}

.search-input {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 10px 12px;
  min-width: 200px;
  outline: none;
}

.sort-select {
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 10px 12px;
  min-width: 120px;
  outline: none;
  background: #fff;
  color: #374151;
}

.write-btn {
  padding: 10px 14px;
  border-radius: 12px;
  background: #7c3aed;
  color: #fff;
  font-weight: 700;
  box-shadow: 0 10px 20px rgba(124, 58, 237, 0.2);
  transition: all 0.15s ease;
}

.write-btn:hover {
  filter: brightness(1.05);
}

.table-wrapper {
  margin-top: 12px;
}

.table-header,
.table-row {
  display: grid;
  grid-template-columns: 80px 1fr 180px 140px;
  align-items: center;
}

.table-header {
  background: #f3f4f6;
  padding: 12px 14px;
  color: #374151;
  font-weight: 700;
  border: 1px solid #e5e7eb;
  border-radius: 14px 14px 0 0;
}

.table-rows {
  list-style: none;
  margin: 0;
  padding: 0;
  border: 1px solid #e5e7eb;
  border-top: none;
  border-radius: 0 0 14px 14px;
  overflow: hidden;
}

.table-row {
  padding: 12px 14px;
  border-top: 1px solid #f1f5f9;
  cursor: pointer;
  transition: background 0.15s ease;
}

.table-row:hover {
  background: #f8fafc;
}

.title-text {
  font-weight: 700;
  color: #1f2937;
}

.badge {
  display: inline-block;
  background: #e1f4ea;
  color: #2f855a;
  padding: 4px 8px;
  border-radius: 10px;
  font-size: 12px;
  font-weight: 700;
  margin-top: 4px;
}

.empty {
  padding: 18px;
  text-align: center;
  color: #6b7280;
  border: 1px solid #e5e7eb;
  border-radius: 14px;
  margin-top: 10px;
}

.empty.error {
  color: #dc2626;
}

@media (max-width: 768px) {
  .table-header,
  .table-row {
    grid-template-columns: 70px 1fr;
    row-gap: 4px;
  }
  .col-author,
  .col-date {
    display: none;
  }
}
</style>
