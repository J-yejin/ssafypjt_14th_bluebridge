<template>
  <div class="min-h-[calc(100vh-5rem)]">
    <!-- Hero -->
    <div class="max-w-[1400px] mx-auto px-8 lg:px-12 py-20">
      <div class="text-center mb-20">
        <div class="inline-block mb-6">
          <span class="px-4 py-2 bg-blue-100 text-blue-700 rounded-full text-sm">청년을 위한 정책 큐레이션</span>
        </div>
        <h1 class="text-blue-900 mb-6 text-5xl lg:text-6xl leading-tight">
          필요한 정책을,
          <br />
          <span class="bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">지금 바로 찾아보세요</span>
        </h1>
        <p class="text-gray-600 text-lg max-w-3xl mx-auto leading-relaxed">
          Blue Bridge는 전국의 청년 정책을 한 곳에 모아 쉽고 빠르게 탐색할 수 있도록 돕습니다.
          AI 기반 추천으로 나에게 맞는 정책을 바로 확인하세요.
        </p>
      </div>

      <!-- CTA Cards -->
      <div class="grid lg:grid-cols-2 gap-8 max-w-6xl mx-auto mb-24">
        <router-link
          to="/browse"
          class="group bg-white rounded-3xl p-10 shadow-xl hover:shadow-2xl transition-all border border-blue-100 hover:border-blue-200 relative overflow-hidden"
        >
          <div class="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-blue-50 to-transparent rounded-full -mr-32 -mt-32 opacity-50 group-hover:opacity-70 transition-opacity" />
          <div class="relative">
            <div class="w-20 h-20 bg-gradient-to-br from-blue-400 to-blue-600 rounded-2xl flex items-center justify-center mb-8 shadow-lg group-hover:scale-110 transition-transform">
              <Search :size="40" class="text-white" />
            </div>
            <h2 class="text-blue-900 mb-4 text-3xl">정책 검색</h2>
            <p class="text-gray-600 mb-8 text-lg leading-relaxed">
              분야, 지역, 연령대별로 청년 정책을 빠르게 찾아보세요. 카테고리별로 정리된 정책 정보를 한눈에 볼 수 있습니다.
            </p>
            <div class="flex items-center text-blue-600 group-hover:text-blue-700 text-lg">
              <span class="mr-3">정책 찾기 시작하기</span>
              <ArrowRight :size="24" class="group-hover:translate-x-2 transition-transform" />
            </div>
          </div>
        </router-link>

        <router-link
          to="/recommend"
          class="group bg-white rounded-3xl p-10 shadow-xl hover:shadow-2xl transition-all border border-cyan-100 hover:border-cyan-200 relative overflow-hidden"
        >
          <div class="absolute top-0 right-0 w-64 h-64 bg-gradient-to-br from-cyan-50 to-transparent rounded-full -mr-32 -mt-32 opacity-50 group-hover:opacity-70 transition-opacity" />
          <div class="relative">
            <div class="w-20 h-20 bg-gradient-to-br from-cyan-400 to-cyan-600 rounded-2xl flex items-center justify-center mb-8 shadow-lg group-hover:scale-110 transition-transform">
              <Sparkles :size="40" class="text-white" />
            </div>
            <h2 class="text-blue-900 mb-4 text-3xl">맞춤 추천</h2>
            <p class="text-gray-600 mb-8 text-lg leading-relaxed">
              프로필과 관심사를 입력하면 AI가 추천하는 정책을 받을 수 있습니다. RAG 검색으로 궁금한 정책을 자연어로 물어보세요.
            </p>
            <div class="flex items-center text-cyan-600 group-hover:text-cyan-700 text-lg">
              <span class="mr-3">맞춤 추천받기</span>
              <ArrowRight :size="24" class="group-hover:translate-x-2 transition-transform" />
            </div>
          </div>
        </router-link>
      </div>

      <!-- Categories -->
      <div class="bg-white/70 backdrop-blur-sm rounded-3xl p-12 max-w-6xl mx-auto border border-blue-100/50 shadow-lg">
        <div class="text-center mb-10">
          <h3 class="text-blue-900 mb-3 text-3xl">주요 정책 카테고리</h3>
          <p class="text-gray-600">관심 있는 분야를 눌러 정책을 살펴보세요.</p>
        </div>
        <div class="grid grid-cols-2 md:grid-cols-4 gap-5">
          <div
            v-for="category in categories"
            :key="category"
            class="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-2xl p-6 text-center border border-blue-100 hover:shadow-md hover:scale-105 transition-all cursor-pointer group"
          >
            <span class="text-blue-700 text-lg group-hover:text-blue-800">{{ category }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Stats -->
    <div class="bg-gradient-to-r from-blue-600 to-cyan-600 py-16">
      <div class="max-w-[1400px] mx-auto px-8 lg:px-12">
        <div class="grid md:grid-cols-3 gap-12 text-center text-white">
          <div>
            <div class="text-5xl mb-3 opacity-90">500+</div>
            <div class="text-blue-100 text-lg">등록된 청년 정책</div>
          </div>
          <div>
            <div class="text-5xl mb-3 opacity-90">50,000+</div>
            <div class="text-blue-100 text-lg">누적 이용자</div>
          </div>
          <div>
            <div class="text-5xl mb-3 opacity-90">98%</div>
            <div class="text-blue-100 text-lg">만족도</div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { Search, Sparkles, ArrowRight } from 'lucide-vue-next';

const categories = ['창업', '주거', '교육', '취업', '문화', '건강', '지역', '농업'];
</script>
