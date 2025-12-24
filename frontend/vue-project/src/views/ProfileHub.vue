<template>
  <div class="min-h-screen">
    <div class="max-w-[1100px] mx-auto px-8 lg:px-12 py-12">
      <div class="mb-12 text-center">
        <h1 class="text-blue-900 mb-3 text-4xl">프로필</h1>
        <p class="text-gray-600 text-lg">마이 페이지와 나의 관심정책 중 원하는 메뉴를 선택하세요.</p>
      </div>

      <div class="grid md:grid-cols-2 gap-8">
        <router-link
          to="/profile/edit"
          class="group rounded-3xl p-10 border border-green-200 bg-gradient-to-br from-green-50 via-green-100 to-emerald-100 shadow-lg hover:shadow-2xl transition-all"
        >
          <div class="flex items-center gap-4 mb-6">
            <div class="w-14 h-14 rounded-2xl bg-green-500 flex items-center justify-center shadow-md">
              <User :size="26" class="text-white" />
            </div>
            <div>
              <h2 class="text-2xl text-green-900 font-semibold">마이 페이지</h2>
              <p class="text-green-700">내 정보를 확인하고 수정할 수 있어요.</p>
            </div>
          </div>
          <div class="text-green-800 text-lg">
            프로필을 완성하면 맞춤 정책 추천 정확도가 올라갑니다.
          </div>
        </router-link>

        <router-link
          to="/profile/wishlist"
          class="group rounded-3xl p-10 border border-blue-200 bg-gradient-to-br from-blue-50 via-sky-100 to-cyan-100 shadow-lg hover:shadow-2xl transition-all"
        >
          <div class="flex items-center gap-4 mb-6">
            <div class="w-14 h-14 rounded-2xl bg-green-500 flex items-center justify-center shadow-md">
              <Heart :size="26" class="text-white" />
            </div>
            <div>
              <h2 class="text-2xl text-blue-900 font-semibold">나의 관심정책</h2>
              <p class="text-blue-700">찜한 정책을 한 번에 모아볼 수 있어요.</p>
            </div>
          </div>
          <div class="text-blue-800 text-lg">
            여러 정책들을 모아 비교할 수 있습니다.
          </div>
        </router-link>
      </div>
    </div>
  </div>
</template>

<script setup>
import { User, Heart } from 'lucide-vue-next';
</script>








