<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 via-sky-50 to-cyan-50">
    <Navbar />
    <router-view />
  </div>
</template>

<script setup>
import Navbar from './components/Navbar.vue';
</script>
