<template>
  <nav class="bg-white/90 backdrop-blur-lg border-b-2 border-blue-100/60 sticky top-0 z-50 shadow-md">
    <div class="max-w-[1400px] mx-auto px-8 lg:px-12">
      <div class="flex justify-between items-center h-24">
        <router-link to="/" class="flex items-center gap-3 group">
          <img
            src="/logo.png"
            alt="Blue Bridge 로고"
            class="w-24 h-20 transition-all object-contain"
          />
          <div class="flex flex-col leading-tight">
            <span class="text-lg text-gray-600 font-medium">청년 정책 허브</span>
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
            <span>홈</span>
          </router-link>

          <router-link
            to="/browse"
            :class="[
              'flex items-center gap-2 px-5 py-3 rounded-lg transition-all',
              isActive('/browse') ? 'bg-blue-50 text-blue-700' : 'text-gray-600 hover:bg-blue-50/50 hover:text-blue-600'
            ]"
          >
            <Search :size="18" />
            <span>정책 찾기</span>
          </router-link>

          <router-link
            to="/recommend"
            :class="[
              'flex items-center gap-2 px-5 py-3 rounded-lg transition-all',
              isActive('/recommend') ? 'bg-blue-50 text-blue-700' : 'text-gray-600 hover:bg-blue-50/50 hover:text-blue-600'
            ]"
          >
            <Sparkles :size="18" />
            <span>정책 추천</span>
          </router-link>

          <router-link
            to="/boards"
            :class="[
              'flex items-center gap-2 px-5 py-3 rounded-lg transition-all',
              isActive('/boards') ? 'bg-blue-50 text-blue-700' : 'text-gray-600 hover:bg-blue-50/50 hover:text-blue-600'
            ]"
          >
            <Search :size="18" />
            <span>게시글</span>
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
              로그아웃
            </button>
          </template>
          <template v-else>
            <router-link
              to="/login"
              class="px-4 py-3 rounded-lg text-gray-700 hover:bg-blue-50 transition-all border border-gray-200"
            >
              로그인
            </router-link>
            <router-link
              to="/signup"
              class="px-4 py-3 rounded-lg text-white accent-button shadow-md hover:shadow-lg transition-all"
            >
              회원가입
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
import { Search, Sparkles, User, Home } from 'lucide-vue-next';
import { useAuthStore } from '../stores/authStore';
import { useUserStore } from '../stores/userStore';

const route = useRoute();
const router = useRouter();
const isActive = (path) => computed(() => route.path === path).value;
const isProfileActive = computed(() => route.path.startsWith('/profile'));
const authStore = useAuthStore();
const userStore = useUserStore();
const isLoggedIn = computed(() => authStore.isAuthenticated);
const profileLabel = computed(() => (userStore.isProfileComplete ? '마이 프로필' : '프로필 설정'));

const handleLogout = () => {
  authStore.clearTokens();
  userStore.resetProfile();
  router.push('/');
};
</script>
