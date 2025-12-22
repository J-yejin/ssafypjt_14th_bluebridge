<template>
  <div class="min-h-screen">
    <div class="max-w-[1200px] mx-auto px-8 lg:px-12 py-12">
      <router-link
        to="/browse"
        class="flex items-center gap-2 text-blue-600 hover:text-blue-700 mb-8 inline-flex px-4 py-2 hover:bg-blue-50 rounded-lg transition-all"
      >
        <ArrowLeft :size="20" />
        <span class="text-lg">목록으로 돌아가기</span>
      </router-link>

      <div v-if="loading" class="bg-white rounded-2xl p-12 text-center shadow-lg text-gray-600">
        정책을 불러오는 중입니다...
      </div>

      <div v-else-if="!policy" class="bg-white rounded-2xl p-12 text-center shadow-lg">
        <p class="text-gray-600 text-lg">정책 정보를 찾을 수 없습니다.</p>
        <router-link to="/browse" class="text-blue-600 hover:text-blue-700 mt-6 inline-block text-lg">
          정책 검색으로 돌아가기
        </router-link>
      </div>

      <div v-else class="bg-white rounded-3xl shadow-2xl overflow-hidden">
        <!-- Header -->
        <div class="bg-gradient-to-r from-blue-500 via-blue-600 to-cyan-500 px-12 py-16 text-white relative overflow-hidden">
          <div class="absolute top-0 right-0 w-96 h-96 bg-white/10 rounded-full -mr-48 -mt-48" />
          <div class="absolute bottom-0 left-0 w-80 h-80 bg-white/10 rounded-full -ml-40 -mb-40" />
          <div class="relative">
            <div class="flex items-center gap-4 mb-6">
              <span class="px-5 py-2 bg-white/20 backdrop-blur rounded-xl text-lg">
                {{ policy.category }}
              </span>
              <span class="px-5 py-2 bg-white/20 backdrop-blur rounded-xl text-lg">
                {{ policy.region }}
              </span>
            </div>
            <h1 class="mb-4 text-5xl">{{ policy.title }}</h1>
            <p class="text-blue-50 text-xl">{{ policy.organization }}</p>
          </div>
        </div>

        <!-- Content -->
        <div class="px-12 py-12">
          <!-- Quick Info -->
          <div class="grid md:grid-cols-2 gap-6 mb-12 p-8 bg-gradient-to-br from-blue-50 to-cyan-50 rounded-2xl border border-blue-100">
            <div class="flex items-center gap-4">
              <div class="w-14 h-14 bg-blue-500 rounded-xl flex items-center justify-center flex-shrink-0 shadow-md">
                <Calendar :size="28" class="text-white" />
              </div>
              <div>
                <p class="text-gray-500 mb-1">신청 기간</p>
                <p class="text-gray-900 text-lg">{{ policy.applicationPeriod }}</p>
              </div>
            </div>
            <div class="flex items-center gap-4">
              <div class="w-14 h-14 bg-cyan-500 rounded-xl flex items-center justify-center flex-shrink-0 shadow-md">
                <Users :size="28" class="text-white" />
              </div>
              <div>
                <p class="text-gray-500 mb-1">연령</p>
                <p class="text-gray-900 text-lg">
                  {{ policy.ageRange === '제한없음' ? '제한없음' : `${policy.ageRange}세` }}
                </p>
              </div>
            </div>
          </div>

          <!-- Description -->
          <section class="mb-12">
            <h2 class="text-blue-900 mb-6 text-3xl border-l-4 border-blue-500 pl-6">정책 소개</h2>
            <p class="text-gray-700 leading-relaxed text-lg pl-6">{{ policy.description }}</p>
          </section>

          <!-- Eligibility -->
          <section class="mb-12">
            <h2 class="text-blue-900 mb-6 text-3xl border-l-4 border-blue-500 pl-6">신청 자격</h2>
            <div class="pl-6 grid md:grid-cols-2 gap-4">
              <div
                v-for="(item, index) in policy.eligibility"
                :key="index"
                class="flex items-start gap-3 bg-gray-50 p-4 rounded-xl"
              >
                <CheckCircle2 :size="22" class="text-green-600 mt-0.5 flex-shrink-0" />
                <p class="text-gray-700 text-lg leading-snug">{{ item }}</p>
              </div>
            </div>
          </section>

          <!-- Benefits -->
          <section class="mb-12">
            <h2 class="text-blue-900 mb-6 text-3xl border-l-4 border-blue-500 pl-6">지원 내용</h2>
            <div class="bg-gradient-to-br from-blue-50 via-cyan-50 to-blue-50 rounded-2xl p-8 border-2 border-blue-200 shadow-inner">
              <p class="text-gray-800 text-lg leading-relaxed">{{ policy.benefits }}</p>
            </div>
          </section>

          <!-- Tags -->
          <section class="mb-12">
            <h2 class="text-blue-900 mb-6 text-3xl border-l-4 border-blue-500 pl-6">관련 키워드</h2>
            <div class="flex flex-wrap gap-3 pl-6">
              <span
                v-for="tag in policy.tags"
                :key="tag"
                class="px-5 py-2.5 bg-blue-100 text-blue-700 rounded-xl text-lg hover:bg-blue-200 transition-colors cursor-pointer"
              >
                #{{ tag }}
              </span>
            </div>
          </section>

          <!-- CTA -->
          <div class="flex gap-6 pt-8 border-t-2 border-gray-100">
            <button class="flex-1 bg-gradient-to-r from-blue-500 to-cyan-500 text-white px-10 py-5 rounded-2xl hover:shadow-2xl transition-all flex items-center justify-center gap-3 text-lg shadow-lg">
              <ExternalLink :size="24" />
              <span>신청 페이지로 이동</span>
            </button>
            <button class="px-10 py-5 border-2 border-blue-500 text-blue-600 rounded-2xl hover:bg-blue-50 transition-all text-lg">
              공유하기
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { ArrowLeft, Calendar, Users, CheckCircle2, ExternalLink } from 'lucide-vue-next';
import { usePolicyStore } from '../stores/policyStore';

const route = useRoute();
const policyStore = usePolicyStore();

const policyId = computed(() => route.params.id);
const policy = computed(() => policyStore.getById(policyId.value));
const loading = computed(() => policyStore.loading);

onMounted(() => {
  if (!policy.value) {
    policyStore.loadPolicyById(policyId.value);
  }
});
</script>
