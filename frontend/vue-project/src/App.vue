<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<template>
  <div class="app-shell">
    <header class="topbar">
      <div class="brand">
        <span class="dot"></span>
        <span class="title">BlueBridge</span>
      </div>
      <nav class="nav">
        <RouterLink to="/">홈</RouterLink>
      </nav>
    </header>

    <main class="page">
      <RouterView />
    </main>
  </div>
</template>

<style scoped>
.app-shell {
  min-height: 100vh;
  background: linear-gradient(135deg, #f6f9ff 0%, #ffffff 40%, #f2f6ff 100%);
  color: #0f172a;
}

.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  border-bottom: 1px solid #e5e7eb;
  background: rgba(255, 255, 255, 0.85);
  backdrop-filter: blur(10px);
  position: sticky;
  top: 0;
  z-index: 10;
}

.brand {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  font-weight: 700;
  font-size: 18px;
  letter-spacing: -0.01em;
}

.dot {
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: radial-gradient(circle at 30% 30%, #2563eb, #1e40af);
  box-shadow: 0 0 12px rgba(37, 99, 235, 0.5);
}

.nav {
  display: inline-flex;
  gap: 12px;
  font-weight: 600;
}

.nav a {
  padding: 8px 12px;
  border-radius: 8px;
  color: #0f172a;
  text-decoration: none;
  transition: background-color 0.2s ease, color 0.2s ease;
}

.nav a:hover {
  background-color: #e0e7ff;
  color: #1d4ed8;
}

.nav a.router-link-exact-active {
  background-color: #2563eb;
  color: #ffffff;
}

.page {
  padding: 32px 24px 48px;
}

@media (min-width: 768px) {
  .page {
    padding: 48px 56px 64px;
  }
}
</style>
