<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 via-cyan-50 to-white flex flex-col">
    <Navbar />
    <main class="flex-1">
      <router-view />
    </main>
    <SiteFooter />
  </div>
</template>

<script setup>
import Navbar from './components/Navbar.vue';
import SiteFooter from './components/SiteFooter.vue';
</script>
