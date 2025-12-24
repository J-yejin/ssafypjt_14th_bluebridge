<template>
  <div class="landing">
    <!-- Hero -->
    <section class="hero">
      <div class="hero-left card">
        <div class="eyebrow">이벤트</div>
        <h1>
          청년 정책 신규 가입<br />
          혜택 안내
        </h1>
        <p class="body">
          한 번의 가입으로 맞춤 알림을 받아 보고<br />
          신청 기간을 놓치지 마세요.
        </p>
        <div class="actions">
          <button class="btn primary" @click="goRecommend">맞춤 알림 받기</button>
          <button class="btn ghost" @click="goBrowse">정책 둘러보기</button>
        </div>
      </div>

      <div class="hero-right">
        <div class="card service">
          <p class="eyebrow">빠르고 안전한</p>
          <h3>나의 청년정책 한눈에</h3>
          <div class="service-grid">
            <div class="pill">신청 일정</div>
            <div class="pill">나의 관심정책</div>
          </div>
        </div>
        <div class="card notice">
          <div class="notice-header">
            <p class="eyebrow">알려드립니다</p>
            <h4>정책 신청 일정 사전 안내</h4>
            <p class="date">2025.03 업데이트</p>
          </div>
          <div class="notice-calendar" aria-label="정책 신청 일정">
            <div class="calendar-header">
              <span class="calendar-month">2025.03</span>
              <span class="calendar-legend">
                <span class="calendar-dot" aria-hidden="true"></span>
                신청 일정
              </span>
            </div>
            <div class="calendar-grid">
              <div class="calendar-day">2</div>
              <div class="calendar-day">3</div>
              <div class="calendar-day">4</div>
              <div class="calendar-day event">
                5
                <span class="event-label">접수</span>
              </div>
              <div class="calendar-day">6</div>
              <div class="calendar-day">7</div>
              <div class="calendar-day">8</div>
              <div class="calendar-day">9</div>
              <div class="calendar-day">10</div>
              <div class="calendar-day">11</div>
              <div class="calendar-day event">
                12
                <span class="event-label">마감</span>
              </div>
              <div class="calendar-day">13</div>
              <div class="calendar-day">14</div>
              <div class="calendar-day">15</div>
            </div>
          </div>
        </div>
      </div>
    </section>

    <!-- Feature highlights -->
    <section class="features">
      <div class="section-title">
        <h2>신뢰와 안정의 정책 허브</h2>
        <p>여러 기관의 정책을 한 번에 확인하고, 맞춤 추천을 받아보세요.</p>
      </div>
      <div class="feature-grid">
        <div
          v-for="card in featureCards"
          :key="card.title"
          class="card feature"
          :class="card.className"
        >
          <img v-if="card.image" :src="card.image" :alt="card.title" class="feature-img" />
          <div v-else class="icon">{{ card.fallback }}</div>
          <h3>{{ card.title }}</h3>
          <p>{{ card.desc }}</p>
        </div>
      </div>
    </section>

    <!-- Banner CTAs -->
    <section class="banners">
      <div class="banner card">
        <div>
          <p class="eyebrow">미리 체험하기</p>
          <h3>정책 브리핑 맛보기</h3>
          <p>관심 분야를 선택하면 샘플 브리핑을 보여드립니다.</p>
        </div>
        <button class="btn primary">샘플 보기</button>
      </div>
      <div class="banner card">
        <div>
          <p class="eyebrow">온라인 신청</p>
          <h3>신청 링크 바로가기</h3>
          <p>지원 대상 확인 후, 한 번에 신청 페이지로 이동하세요.</p>
        </div>
        <button class="btn ghost">신청 링크 모아보기</button>
      </div>
    </section>

    <!-- Partner / categories -->
    <section class="partners card">
      <div class="section-title compact">
        <h2>나만의 정책 파트너</h2>
        <p>카테고리별 맞춤 정책을 빠르게 탐색하세요.</p>
      </div>
      <div class="partner-grid">
        <div class="partner-tile">
          <div class="bubble mint">💼</div>
          <span>취업·창업</span>
        </div>
        <div class="partner-tile">
          <div class="bubble blue">🏠</div>
          <span>주거·대출</span>
        </div>
        <div class="partner-tile">
          <div class="bubble sand">🎓</div>
          <span>교육·훈련</span>
        </div>
        <div class="partner-tile">
          <div class="bubble coral">🧡</div>
          <span>복지·의료</span>
        </div>
        <div class="partner-tile">
          <div class="bubble purple">💳</div>
          <span>금융·지원금</span>
        </div>
        <div class="partner-tile">
          <div class="bubble gray">📑</div>
          <span>기타 서비스</span>
        </div>
      </div>
    </section>

    <!-- Info grid -->
    <section class="info-grid">
      <div class="card list-card">
        <div class="list-header">
          <h3>공지사항</h3>
          <a href="#">더보기</a>
        </div>
        <ul>
          <li>
            <span>정책 데이터 업데이트 안내</span>
            <span class="date">2025.03.01</span>
          </li>
          <li>
            <span>맞춤 추천 베타 오픈</span>
            <span class="date">2025.02.20</span>
          </li>
          <li>
            <span>서비스 점검 일정 안내</span>
            <span class="date">2025.02.05</span>
          </li>
        </ul>
      </div>

      <div class="card list-card">
        <div class="list-header">
          <h3>자료실</h3>
          <a href="#">더보기</a>
        </div>
        <ul>
          <li>
            <span>정책 신청 체크리스트</span>
            <span class="tag">PDF</span>
          </li>
          <li>
            <span>연령·소득 기준 정리표</span>
            <span class="tag">XLSX</span>
          </li>
          <li>
            <span>지역별 지원 요약</span>
            <span class="tag">PDF</span>
          </li>
        </ul>
      </div>

      <div class="card contact">
        <div>
          <p class="eyebrow">고객센터</p>
          <h3>1577-5500</h3>
          <p class="body">평일 09:00 ~ 17:45 (주말·공휴일 휴무)</p>
        </div>
        <div class="contact-actions">
          <button class="btn ghost small">1:1 문의</button>
          <button class="btn primary small">FAQ</button>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';

const router = useRouter();
const goBrowse = () => router.push('/browse');
const goRecommend = () => router.push('/recommend');

// 이미지가 없으면 fallback 이모지 사용
const featureCards = [
  {
    title: '기관별 정책 모음',
    desc: '정부·지자체·용책을 한 곳에.',
    className: 'mint',
    image: '/feature-org.png', // public/feature-org.png
    fallback: '🏦',
  },
  {
    title: '신청 일정 알림',
    desc: '마감일 이전에 미리 알림을 받아보세요.',
    className: 'sand',
    image: '/feature-calendar.png', // public/feature-calendar.png
    fallback: '📅',
  },
  {
    title: '맞춤 추천',
    desc: '프로필 기반으로 꼭 맞는 정책 찾기.',
    className: 'purple',
    image: '/feature-recommend.png', // public/feature-recommend.png
    fallback: '🔍',
  },
];
</script>

<style scoped>
:global(body) {
  background: #f5fbf1;
  color: #0f172a;
  font-family: 'Pretendard', 'Inter', 'Noto Sans KR', system-ui, -apple-system, sans-serif;
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
  font-size: 12px;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: #66c08c;
}

.hero-left .eyebrow {
  color: #d7f4df;
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

.service h3 {
  margin: 6px 0 10px;
  font-size: 22px;
  color: #0f172a;
}

.service-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 8px;
  margin: 10px 0;
}

.pill {
  background: #ecf7e9;
  color: #2f7c46;
  padding: 10px 12px;
  border-radius: 12px;
  text-align: center;
  font-weight: 600;
  font-size: 14px;
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

.calendar-grid {
  display: grid;
  grid-template-columns: repeat(7, minmax(0, 1fr));
  gap: 6px;
  font-size: 12px;
  color: #475569;
}

.calendar-day {
  min-height: 32px;
  border-radius: 8px;
  display: grid;
  place-items: center;
  background: #ffffff;
  border: 1px solid #e2e8f0;
}

.calendar-day.event {
  border-color: #34d399;
  background: #ecfdf5;
  color: #047857;
  font-weight: 700;
}

.event-label {
  display: block;
  font-size: 10px;
  margin-top: 2px;
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
  grid-template-columns: 2fr 2fr 1.4fr;
  gap: 12px;
}

.list-card {
  padding: 18px;
  display: grid;
  gap: 12px;
  text-align: center;
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
}

.list-card ul {
  list-style: none;
  padding: 0;
  margin: 0;
  display: grid;
  gap: 10px;
}

.list-card li {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
  color: #1f2937;
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
