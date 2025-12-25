<template>
  <div class="landing">
    <!-- Hero -->
    <section class="hero">
      <div class="hero-left card">
        <h1>한눈에 보는 청년 정책<br />맞춤 추천까지 받아보세요</h1>
        <p class="body">
          조건에 맞는 정책을 빠르게 찾아보고<br />
          신청 기한까지 놓치지 마세요.
        </p>
        <img src="/feature-home-big.png" alt="정책 브리핑" class="hero-illustration" />
        <div class="actions">
          <button class="btn primary" @click="goRecommend">맞춤 추천 받기</button>
          <button class="btn ghost" @click="goBrowse">정책 둘러보기</button>
        </div>
      </div>

      <!-- Calendar -->
      <div class="hero-right">
        <div class="card notice">
          <div class="notice-header">
            <p class="eyebrow">즐겨찾기 일정</p>
            <h4>{{ currentYear }}년 {{ currentMonth }}월</h4>
            <p class="date">즐겨찾기한 정책의 신청 기간을 확인하세요.</p>
          </div>
          <div class="notice-calendar" aria-label="즐겨찾기 일정 달력">
            <div class="calendar-header">
              <button class="nav-btn" @click="changeMonth(-1)">‹</button>
              <span class="calendar-month">{{ currentYear }}.{{ currentMonthString }}</span>
              <button class="nav-btn" @click="changeMonth(1)">›</button>
              <span class="calendar-legend">
                <span class="calendar-dot" aria-hidden="true"></span>
                일정
              </span>
            </div>
            <div class="weekday-row">
              <span v-for="w in weekdays" :key="w" class="weekday">{{ w }}</span>
            </div>
            <div class="calendar-grid">
              <div
                v-for="(day, idx) in calendarDays"
                :key="idx"
                class="calendar-cell"
                :class="{ empty: !day, 'has-events': day?.events?.length }"
              >
                <div v-if="day" class="day-number">{{ day.day }}</div>
                <div v-if="day && day.events.length" class="event-marker">
                  <span class="event-dot" aria-hidden="true"></span>
                  <div class="event-tooltip">
                    <div class="tooltip-title">오늘의 정책 일정</div>
                    <ul>
                      <li v-for="(event, i) in day.events" :key="i">
                        <span class="event-title">{{ event.title }}</span>
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
            <div v-if="openEndedEvents.length" class="open-ended">
              <div class="open-ended-title">상시 모집</div>
              <div class="open-ended-list">
                <div v-for="(ev, idx) in openEndedEvents" :key="idx" class="open-ended-item">
                  <span class="event-title">{{ ev.title }}</span>
                  <span class="event-range">상시 모집</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Feature highlights -->
    <section class="features">
      <div class="section-title">
        <h2>한눈에 보는 정책</h2>
        <p>분야별로 빠르게 살펴보고, 맞춤 추천까지 받아보세요.</p>
      </div>
      <div class="feature-grid">
        <div v-for="card in featureCards" :key="card.title" class="card feature" :class="card.className">
          <img v-if="card.image" :src="card.image" :alt="card.title" class="feature-img" />
          <div v-else class="icon">{{ card.fallback }}</div>
          <h3>{{ card.title }}</h3>
          <p>{{ card.desc }}</p>
        </div>
      </div>
    </section>

    <!-- Partner / categories -->
    <section class="partners card">
      <div class="section-title compact">
        <h2>분야별 정책 큐레이션</h2>
        <p>카테고리별로 맞춤 정책을 빠르게 탐색하세요.</p>
      </div>
      <div class="partner-grid">
        <div class="partner-tile" v-for="cat in categories" :key="cat.label">
          <div class="bubble" :class="cat.className">{{ cat.icon }}</div>
          <span>{{ cat.label }}</span>
        </div>
      </div>
    </section>

    <!-- Info grid: boards 연동 -->
    <section class="info-grid">
      <div class="card list-card">
        <div class="list-header">
          <h3>공지사항</h3>
          <button class="link-btn" @click="goBoardCategory('notice')">더보기</button>
        </div>
        <ul>
          <li v-for="item in noticeList" :key="item.id">
            <button type="button" class="board-link" @click="goBoardDetail(item.id)">
              {{ item.title }}
            </button>
            <span class="date">{{ formatDate(item.created_at) }}</span>
          </li>
          <li v-if="!noticeList.length" class="empty">등록된 공지사항이 없습니다.</li>
        </ul>
      </div>

      <div class="card list-card">
        <div class="list-header">
          <h3>자료실</h3>
          <button class="link-btn" @click="goBoardCategory('review')">더보기</button>
        </div>
        <ul>
          <li v-for="item in resourceList" :key="item.id">
            <button type="button" class="board-link" @click="goBoardDetail(item.id)">
              {{ item.title }}
            </button>
            <span class="date">{{ formatDate(item.created_at) }}</span>
          </li>
          <li v-if="!resourceList.length" class="empty">등록된 자료가 없습니다.</li>
        </ul>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { usePolicyStore } from '../stores/policyStore';
import { useAuthStore } from '../stores/authStore';
import { useBoardStore } from '../stores/boardStore';

const router = useRouter();
const policyStore = usePolicyStore();
const authStore = useAuthStore();
const boardStore = useBoardStore();

const goBrowse = () => router.push('/browse');
const goRecommend = () => router.push('/recommend');

const currentDate = ref(new Date());
const currentYear = computed(() => currentDate.value.getFullYear());
const currentMonth = computed(() => currentDate.value.getMonth() + 1);
const currentMonthString = computed(() => currentMonth.value.toString().padStart(2, '0'));
const weekdays = ['일', '월', '화', '수', '목', '금', '토'];

const cachedPolicies = ref([]);

const wishlistPolicies = computed(() =>
  policyStore.policies.filter((p) => policyStore.isWishlisted(p.id))
);

// 달력 이벤트 (기간 있음)
const calendarPolicies = computed(() => {
  const normalize = (list = []) =>
    list
      .filter((p) => p.startDate && p.endDate)
      .map((p) => ({
        title: p.title,
        startDate: p.startDate,
        endDate: p.endDate,
      }));

  const combined = [...normalize(wishlistPolicies.value), ...normalize(cachedPolicies.value)];
  const seen = new Set();
  return combined.filter((p) => {
    if (seen.has(p.title)) return false;
    seen.add(p.title);
    return true;
  });
});

// 상시 모집 (기간 없음)
const openEndedEvents = computed(() => {
  const isAlways = (p) => !p.startDate && !p.endDate;
  const combined = [
    ...(wishlistPolicies.value || []).filter(isAlways),
    ...(cachedPolicies.value || []).filter(isAlways),
  ];
  const seen = new Set();
  return combined.filter((p) => {
    if (seen.has(p.title)) return false;
    seen.add(p.title);
    return true;
  });
});

const parseDate = (value) => {
  if (!value) return null;
  const d = new Date(value);
  return Number.isNaN(d.getTime()) ? null : d;
};

const eventsForMonth = computed(() => {
  const first = new Date(currentYear.value, currentMonth.value - 1, 1);
  const last = new Date(currentYear.value, currentMonth.value, 0, 23, 59, 59);
  const events = [];
  calendarPolicies.value.forEach((p) => {
    const s = parseDate(p.startDate);
    const e = parseDate(p.endDate);
    const start = s || e;
    const end = e || s;
    if (!start && !end) return;
    const startInRange = start && start <= last;
    const endInRange = end && end >= first;
    if (startInRange && endInRange) {
      events.push({
        title: p.title,
        start,
        end,
      });
    }
  });
  return events;
});

const calendarDays = computed(() => {
  const daysInMonth = new Date(currentYear.value, currentMonth.value, 0).getDate();
  const firstWeekday = new Date(currentYear.value, currentMonth.value - 1, 1).getDay();
  const cells = [];
  for (let i = 0; i < firstWeekday; i += 1) cells.push(null);
  for (let day = 1; day <= daysInMonth; day += 1) {
    const dayEvents = eventsForMonth.value.filter((ev) => {
      const d = new Date(currentYear.value, currentMonth.value - 1, day);
      return ev.start <= d && ev.end >= d;
    });
    cells.push({ day, events: dayEvents.map((ev) => ({ title: ev.title })) });
  }
  return cells;
});

const changeMonth = (delta) => {
  const d = new Date(currentDate.value);
  d.setMonth(d.getMonth() + delta);
  currentDate.value = d;
};

// 게시판 연동
const noticeList = computed(() =>
  (boardStore.boards || [])
    .filter((b) => b.category === 'notice')
    .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    .slice(0, 3)
);

const resourceList = computed(() =>
  (boardStore.boards || [])
    .filter((b) => b.category === 'review')
    .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
    .slice(0, 3)
);

const goBoardCategory = (cat) => {
  if (!authStore.isAuthenticated) {
    alert('로그인이 필요합니다.');
    router.push('/login');
    return;
  }
  router.push({ path: '/boards', query: { category: cat } });
};

const goBoardDetail = (id) => {
  if (!authStore.isAuthenticated) {
    alert('로그인이 필요합니다.');
    router.push('/login');
    return;
  }
  router.push(`/boards/${id}`);
};

const formatDate = (value) => {
  if (!value) return '';
  return new Date(value).toLocaleDateString();
};

onMounted(async () => {
  // 캘린더 캐시 로드
  try {
    const cached = JSON.parse(localStorage.getItem('bb_calendar_cache') || '[]');
    if (Array.isArray(cached)) cachedPolicies.value = cached;
  } catch (_) {
    cachedPolicies.value = [];
  }

  if (authStore.isAuthenticated) {
    await policyStore.loadWishlist();
    const ids = Array.isArray(policyStore.wishlistIds) ? policyStore.wishlistIds : [];
    for (const id of ids) {
      await policyStore.loadPolicyById(id);
    }
    const toCache = wishlistPolicies.value.map((p) => ({
      title: p.title,
      startDate: p.startDate,
      endDate: p.endDate,
    }));
    localStorage.setItem('bb_calendar_cache', JSON.stringify(toCache));
    cachedPolicies.value = toCache;
  }

  policyStore.loadPolicies({ force: true });
  boardStore.loadBoards();
});

const featureCards = [
  {
    title: '기관별 정책 모음',
    desc: '취업·주거·교육·금융 정책을 한 곳에.',
    className: 'mint',
    image: '/feature-org.png',
    fallback: '🏛️',
  },
  {
    title: '신청 기간 캘린더',
    desc: '신청 마감 전 알림을 받아보세요.',
    className: 'sand',
    image: '/feature-calendar.png',
    fallback: '🗓️',
  },
  {
    title: '맞춤 추천',
    desc: '프로필 기반으로 꼭 맞는 정책 추천.',
    className: 'purple',
    image: '/feature-recommend.png',
    fallback: '✨',
  },
];

const categories = [
  { label: '취업·창업', icon: '👩‍💼', className: 'mint' },
  { label: '주거·생활', icon: '🏠', className: 'blue' },
  { label: '교육·훈련', icon: '🎓', className: 'sand' },
  { label: '복지·법률', icon: '❤️', className: 'coral' },
  { label: '금융·지원금', icon: '💰', className: 'purple' },
  { label: '기타', icon: '⭐', className: 'gray' },
];
</script>

<style scoped>
:global(body) {
  background: #f5fbf1;
  color: #0f172a;
  font-family: 'NanumSquareNeo', 'NanumSquareNeoBold', 'NanumSquareNeoLight', system-ui, -apple-system, sans-serif;
}

.landing {
  display: flex;
  flex-direction: column;
  gap: 32px;
  padding: 24px;
  text-align: center;
}

.hero,
.features,
.banners,
.partners,
.info-grid {
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
}

.card {
  background: #fff;
  border-radius: 18px;
  box-shadow: 0 16px 40px rgba(15, 23, 42, 0.08);
  border: 1px solid #e5e7eb;
}

.hero {
  display: grid;
  grid-template-columns: 1.6fr 1fr;
  gap: 16px;
}

.hero-left {
  padding: 32px;
  background: linear-gradient(135deg, #c5f5b1 0%, #7fcf92 100%);
  color: #fff;
  text-align: center;
  position: relative;
  overflow: hidden;
}

.hero-left h1 {
  margin: 8px 0 12px;
  font-size: 32px;
  line-height: 1.2;
}

.body {
  margin: 0;
  font-size: 15px;
  line-height: 1.6;
  color: inherit;
}

.eyebrow {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #66c08c;
}

.hero-left .eyebrow {
  color: #d7f4df;
}

.hero-illustration {
  width: 100%;
  max-width: 1000px;
  margin: 1px auto 0;
  display: block;
  filter: drop-shadow(0 12px 24px rgba(0, 0, 0, 0.15));
}

.actions {
  display: flex;
  gap: 10px;
  margin-top: 18px;
  justify-content: center;
}

.btn {
  border: none;
  cursor: pointer;
  border-radius: 12px;
  font-weight: 700;
  padding: 12px 16px;
  transition: transform 0.12s ease, box-shadow 0.12s ease, background 0.12s ease;
}

.btn.primary {
  background: linear-gradient(135deg, #24b47e 0%, #3b82f6 100%);
  color: #fff;
  box-shadow: 0 10px 25px rgba(36, 180, 126, 0.32);
}

.btn.ghost {
  background: #ecf6e8;
  color: #3b8f5a;
  border: 1px solid #c9e7c9;
}

.btn.small {
  padding: 10px 12px;
  font-size: 14px;
}

.btn:hover {
  transform: translateY(-1px);
}

.hero-right {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.hero-right .card {
  padding: 20px;
  text-align: center;
}

.notice h4 {
  margin: 4px 0 6px;
  font-size: 18px;
}

.date {
  color: #64748b;
  font-size: 13px;
}

.notice-header {
  display: grid;
  gap: 4px;
}

.notice-calendar {
  margin-top: 10px;
  background: #f8fafc;
  border-radius: 12px;
  padding: 12px;
  border: 1px solid #e2e8f0;
}

.calendar-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  font-weight: 700;
  color: #334155;
  margin-bottom: 8px;
}

.nav-btn {
  background: #e2e8f0;
  border: none;
  border-radius: 8px;
  padding: 6px 8px;
  cursor: pointer;
  font-weight: 800;
  color: #0f172a;
}

.calendar-legend {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  color: #0f172a;
}

.calendar-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: #34d399;
  box-shadow: 0 0 0 3px rgba(52, 211, 153, 0.2);
}

.weekday-row {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 4px;
  font-size: 12px;
  font-weight: 700;
  color: #475569;
  margin-bottom: 7px;
}

.weekday {
  padding: 5px 0;
  background: #e6edf5;
  border-radius: 7px;
}

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 5px;
}

.calendar-cell {
  min-height: 70px;
  border-radius: 10px;
  background: #ffffff;
  border: 1px solid #e2e8f0;
  padding: 6px;
  text-align: left;
  display: grid;
  gap: 4px;
}

.calendar-cell.empty {
  background: #f8fafc;
}

.day-number {
  font-weight: 800;
  color: #0f172a;
  font-size: 13px;
}

.has-events {
  position: relative;
}

.event-marker {
  position: absolute;
  top: 6px;
  right: 6px;
}

.event-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #22c55e;
  display: inline-block;
  box-shadow: 0 0 0 4px rgba(34, 197, 94, 0.15);
}

.event-tooltip {
  position: absolute;
  top: 18px;
  right: 0;
  background: #0f172a;
  color: #e2e8f0;
  padding: 8px 10px;
  border-radius: 10px;
  min-width: 180px;
  z-index: 10;
  box-shadow: 0 12px 30px rgba(0, 0, 0, 0.2);
  opacity: 0;
  pointer-events: none;
  transform: translateY(4px);
  transition: opacity 0.15s ease, transform 0.15s ease;
}

.event-marker:hover .event-tooltip {
  opacity: 1;
  pointer-events: auto;
  transform: translateY(0);
}

.event-tooltip ul {
  margin: 6px 0 0;
  padding-left: 12px;
  text-align: left;
  display: grid;
  gap: 4px;
  font-size: 12px;
}

.event-tooltip li {
  list-style: disc;
}

.tooltip-title {
  font-weight: 800;
  font-size: 12px;
  margin: 0;
  color: #bbf7d0;
}

.open-ended {
  margin-top: 10px;
  padding: 10px;
  background: #f0fdf4;
  border: 1px solid #34d399;
  border-radius: 10px;
  text-align: left;
}

.open-ended-title {
  font-weight: 800;
  color: #059669;
  margin-bottom: 6px;
}

.open-ended-list {
  display: grid;
  gap: 6px;
}

.open-ended-item {
  padding: 6px;
  border-radius: 8px;
  background: #fff;
  border: 1px solid #d1fae5;
  display: flex;
  justify-content: space-between;
  gap: 8px;
  font-size: 12px;
  color: #065f46;
}

.event-range {
  display: block;
  color: #059669;
  font-weight: 700;
}

.features {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.section-title h2 {
  margin: 0 0 4px;
  font-size: 26px;
}

.section-title p {
  margin: 0;
  color: #64748b;
}

.feature-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 18px;
}

.feature {
  display: grid;
  gap: 12px;
  padding: 32px;
  text-align: center;
  min-height: 240px;
  justify-items: center;
}

.feature .icon {
  font-size: 38px;
}

.feature-img {
  width: 160px;
  height: 160px;
  object-fit: contain;
}

.feature h3 {
  margin: 0;
  font-size: 20px;
}

.feature p {
  margin: 0;
  color: #475569;
  font-size: 15px;
}

.feature.mint {
  background: linear-gradient(135deg, #f7fbff 0%, #e4f2ff 100%);
}
.feature.sand {
  background: linear-gradient(135deg, #fff7e6 0%, #ffe9c7 100%);
}
.feature.purple {
  background: linear-gradient(135deg, #f5f0ff 0%, #e6ddff 100%);
}

.banners {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 12px;
}

.banner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 22px 24px;
  text-align: center;
}

.partners {
  padding: 24px;
}

.partner-grid {
  display: grid;
  grid-template-columns: repeat(6, minmax(0, 1fr));
  gap: 12px;
  margin-top: 16px;
}

.partner-tile {
  background: #f3fbf5;
  border-radius: 14px;
  padding: 16px 12px;
  display: grid;
  justify-items: center;
  gap: 8px;
  border: 1px solid #e5e7eb;
}

.bubble {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: grid;
  place-items: center;
  font-size: 22px;
  color: #0f172a;
}
.bubble.mint {
  background: #def8ef;
}
.bubble.blue {
  background: #d9f1df;
}
.bubble.sand {
  background: #ffeecd;
}
.bubble.coral {
  background: #ffe0d7;
}
.bubble.purple {
  background: #ede7ff;
}
.bubble.gray {
  background: #e2e8f0;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(280px, 1fr));
  gap: 12px;
  max-width: 1200px;
  margin: 0 auto;
  justify-content: center;
}

.list-card {
  padding: 18px;
  display: grid;
  grid-template-rows: auto 1fr;
  gap: 12px;
  text-align: center;
  min-height: 160px;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-weight: 700;
}

.list-header a {
  font-size: 13px;
  color: #3f8c4f;
  text-decoration: none;
  cursor: pointer;
}

.link-btn {
  font-size: 13px;
  color: #3f8c4f;
  background: transparent;
  border: none;
  cursor: pointer;
  font-weight: 700;
}

.board-link {
  background: transparent;
  border: none;
  padding: 0;
  margin: 0;
  color: #1f2937;
  font-size: 14px;
  cursor: pointer;
  text-align: left;
}

.board-link:hover {
  color: #2f855a;
}

.list-card ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 10px;
  align-content: start;
}

.list-card li {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  color: #1f2937;
  align-items: center;
}

.tag {
  background: #e2f3e6;
  color: #2f7c46;
  padding: 4px 8px;
  border-radius: 8px;
  font-weight: 700;
  font-size: 12px;
}

.contact {
  padding: 18px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  text-align: center;
}

.contact h3 {
  margin: 2px 0;
  font-size: 24px;
}

.contact-actions {
  display: flex;
  gap: 8px;
}

@media (max-width: 1024px) {
  .hero {
    grid-template-columns: 1fr;
  }
  .feature-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
  .banners {
    grid-template-columns: 1fr;
  }
  .partner-grid {
    grid-template-columns: repeat(3, minmax(0, 1fr));
  }
  .info-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 640px) {
  .landing {
    padding: 16px;
  }
  .feature-grid {
    grid-template-columns: 1fr;
  }
  .partner-grid {
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }
}
</style>
