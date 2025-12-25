<template>
  <nav class="bg-white/90 backdrop-blur-lg border-b-2 border-blue-100/60 sticky top-0 z-50 shadow-md">
    <div class="max-w-[1400px] mx-auto px-8 lg:px-12">
      <div class="flex justify-between items-center h-24">
        <router-link to="/" class="flex items-center gap-3 group">
          <img
            src="/logo.png"
            alt="Yamujin Policy"
            class="w-24 h-20 transition-all object-contain"
          />
          <div class="flex flex-col leading-tight">
            <span class="text-lg text-gray-600 font-medium">&#52397;&#45380; &#51221;&#52293; &#54728;&#48652;</span>
          </div>
        </router-link>

        <div class="flex gap-2 items-center text-base font-semibold">
          <router-link
            to="/"
            :class="[
              'flex items-center gap-2 px-5 py-3 rounded-lg transition-all',
              isActive('/') ? 'bg-blue-50 text-blue-700' : 'text-gray-600 hover:bg-blue-50/50 hover:text-blue-600'
            ]"
          >
            <Home :size="18" />
            <span>&#54856;</span>
          </router-link>

          <router-link
            to="/browse"
            :class="[
              'flex items-center gap-2 px-5 py-3 rounded-lg transition-all',
              isActive('/browse') ? 'bg-blue-50 text-blue-700' : 'text-gray-600 hover:bg-blue-50/50 hover:text-blue-600'
            ]"
          >
            <Search :size="18" />
            <span>&#51221;&#52293; &#52286;&#44592;</span>
          </router-link>

          <router-link
            to="/recommend"
            :class="[
              'flex items-center gap-2 px-5 py-3 rounded-lg transition-all',
              isActive('/recommend') ? 'bg-blue-50 text-blue-700' : 'text-gray-600 hover:bg-blue-50/50 hover:text-blue-600'
            ]"
          >
            <Sparkles :size="18" />
            <span>&#51221;&#52293; &#52628;&#52380;</span>
          </router-link>

          <router-link
            to="/boards"
            :class="[
              'flex items-center gap-2 px-5 py-3 rounded-lg transition-all',
              isActive('/boards') ? 'bg-blue-50 text-blue-700' : 'text-gray-600 hover:bg-blue-50/50 hover:text-blue-600'
            ]"
          >
            <FileText :size="18" />
            <span>&#44172;&#49884;&#44544;</span>
          </router-link>

          <div class="w-px h-6 bg-gray-200 mx-2" />

          <template v-if="isLoggedIn">
            <router-link
              to="/profile"
              :class="[
                'flex items-center gap-2 px-5 py-3 rounded-lg transition-all',
                isProfileActive ? 'accent-button text-white shadow-md' : 'bg-gray-50 text-gray-700 hover:bg-gray-100'
              ]"
            >
              <User :size="18" />
              <span>{{ profileLabel }}</span>
            </router-link>
            <button
              class="px-4 py-3 rounded-lg text-gray-700 hover:bg-blue-50 transition-all border border-gray-200"
              @click="handleLogout"
            >
              &#47196;&#44536;&#50500;&#50883;
            </button>
          </template>
          <template v-else>
            <router-link
              to="/login"
              class="px-4 py-3 rounded-lg text-gray-700 hover:bg-blue-50 transition-all border border-gray-200"
            >
              &#47196;&#44536;&#51064;
            </router-link>
            <router-link
              to="/signup"
              class="px-4 py-3 rounded-lg text-white accent-button shadow-md hover:shadow-lg transition-all"
            >
              &#54924;&#50896;&#44032;&#51077;
            </router-link>
          </template>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { useRoute, useRouter } from 'vue-router';
import { computed } from 'vue';
import { Search, Sparkles, User, Home, FileText } from 'lucide-vue-next';
import { useAuthStore } from '../stores/authStore';
import { useUserStore } from '../stores/userStore';

const route = useRoute();
const router = useRouter();
const isActive = (path) => computed(() => route.path === path).value;
const isProfileActive = computed(() => route.path.startsWith('/profile'));
const authStore = useAuthStore();
const userStore = useUserStore();
const isLoggedIn = computed(() => authStore.isAuthenticated);
const profileLabel = computed(() => (userStore.isProfileComplete ? '\uB9C8\uC774 \uD398\uC774\uC9C0' : '\uB9C8\uC774 \uD398\uC774\uC9C0'));

const handleLogout = () => {
  authStore.clearTokens();
  userStore.resetProfile();
  router.push('/');
};
</script>
