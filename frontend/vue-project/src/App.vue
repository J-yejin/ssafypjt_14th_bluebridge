<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 via-cyan-50 to-white">
    <Navbar />
    <router-view />
  </div>
</template>

<script setup>
import Navbar from './components/Navbar.vue';
</script>
