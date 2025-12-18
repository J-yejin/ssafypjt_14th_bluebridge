<template>
  <section class="hero">
    <p class="eyebrow">BlueBridge</p>
    <h1>정책/복지/훈련 정보를 한 곳에서</h1>
    <p class="sub">
      백엔드 API가 준비되어 있습니다. 이 화면에서 정책 리스트와 검색, 추천 화면을 점진적으로 붙여갈 예정입니다.
    </p>
    <div class="cta-row">
      <button class="btn primary" type="button">정책 보러가기</button>
      <button class="btn ghost" type="button">추천받기(준비중)</button>
    </div>
  </section>
</template>

<style scoped>
.hero {
  max-width: 880px;
  padding: 40px 32px;
  border-radius: 16px;
  background: #ffffff;
  box-shadow: 0 14px 40px rgba(15, 23, 42, 0.08);
  border: 1px solid #e5e7eb;
}

.eyebrow {
  margin: 0 0 12px;
  font-size: 13px;
  font-weight: 700;
  letter-spacing: 0.08em;
  color: #2563eb;
  text-transform: uppercase;
}

h1 {
  margin: 0 0 14px;
  font-size: 34px;
  line-height: 1.15;
  letter-spacing: -0.02em;
}

.sub {
  margin: 0 0 22px;
  font-size: 16px;
  color: #475569;
  line-height: 1.6;
}

.cta-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.btn {
  padding: 12px 18px;
  border-radius: 12px;
  border: 1px solid #d0d7e2;
  background: #fff;
  color: #0f172a;
  font-weight: 700;
  cursor: pointer;
  transition: transform 0.12s ease, box-shadow 0.12s ease, background 0.12s ease;
}

.btn.primary {
  background: #2563eb;
  color: #fff;
  border-color: #1d4ed8;
  box-shadow: 0 10px 25px rgba(37, 99, 235, 0.25);
}

.btn.ghost:hover {
  background: #f8fafc;
}

.btn.primary:hover {
  background: #1d4ed8;
}

.btn:active {
  transform: translateY(1px);
  box-shadow: none;
}

@media (max-width: 640px) {
  .hero {
    padding: 28px 24px;
  }

  h1 {
    font-size: 28px;
  }
}
</style>
