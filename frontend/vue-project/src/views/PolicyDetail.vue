<template>
  <div class="min-h-screen">
    <div class="max-w-[1200px] mx-auto px-8 lg:px-12 py-12">
      <router-link
        to="/browse"
        class="flex items-center gap-2 text-blue-600 hover:text-blue-700 mb-8 inline-flex px-4 py-2 hover:bg-blue-50 rounded-lg transition-all"
      >
        <ArrowLeft :size="20" />
        <span class="text-lg">정책 목록으로 돌아가기</span>
      </router-link>

      <div v-if="loading" class="bg-white rounded-2xl p-12 text-center shadow-lg text-gray-600">
        정책을 불러오는 중입니다...
      </div>

      <div v-else-if="!policy" class="bg-white rounded-2xl p-12 text-center shadow-lg">
        <p class="text-gray-600 text-lg">정책을 찾을 수 없습니다.</p>
        <router-link to="/browse" class="text-blue-600 hover:text-blue-700 mt-6 inline-block text-lg">
          정책 목록으로 돌아가기
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
                <p class="text-gray-900 text-lg whitespace-pre-line">{{ policy.applicationPeriod }}</p>
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
            <div class="pl-6">
              <div class="bg-gradient-to-br from-blue-50 via-cyan-50 to-blue-50 rounded-2xl p-6 md:p-8 border-2 border-blue-200 shadow-inner">
                <pre class="text-gray-700 leading-relaxed text-base md:text-lg whitespace-pre-wrap break-words overflow-auto w-full max-w-full">
{{ policy.description }}
                </pre>
              </div>
            </div>
          </section>

          <!-- Eligibility -->
          <section class="mb-12">
            <h2 class="text-blue-900 mb-6 text-3xl border-l-4 border-blue-500 pl-6">신청 자격</h2>
            <div class="pl-6 grid md:grid-cols-2 gap-4">
              <div
                v-for="(group, index) in groupedEligibility"
                :key="index"
                class="border border-gray-200 bg-white rounded-xl px-5 py-4 shadow-sm"
              >
                <div class="flex items-start gap-3">
                  <CheckCircle2 :size="20" class="text-green-600 flex-shrink-0 mt-0.5" />
                  <div class="flex-1">
                    <div class="inline-flex items-center bg-green-50 text-green-700 px-3 py-1 rounded-md border border-green-500 text-base font-semibold leading-tight">
                      {{ group.label }}
                    </div>
                    <pre class="mt-2 text-gray-700 text-base leading-relaxed whitespace-pre-wrap break-words overflow-auto w-full max-w-full">
{{ formatEligibility(group) }}
                    </pre>
                  </div>
                </div>
              </div>
            </div>
          </section>

          <!-- Benefits -->
          <section class="mb-12">
            <h2 class="text-blue-900 mb-6 text-3xl border-l-4 border-blue-500 pl-6">지원 내용</h2>
            <div class="bg-gradient-to-br from-blue-50 via-cyan-50 to-blue-50 rounded-2xl p-6 md:p-8 border-2 border-blue-200 shadow-inner">
              <pre class="block w-full text-gray-800 text-base md:text-lg leading-relaxed whitespace-pre-wrap break-words overflow-auto font-sans">
{{ displayBenefits }}
              </pre>
            </div>
          </section>

          <!-- Tags -->
          <section class="mb-12">
            <h2 class="text-blue-900 mb-6 text-3xl border-l-4 border-blue-500 pl-6">관련 키워드</h2>
            <div class="flex flex-wrap gap-3 pl-6">
              <span
                v-if="policy.category"
                class="px-5 py-2.5 bg-blue-100 text-blue-700 rounded-xl text-lg hover:bg-blue-200 transition-colors cursor-pointer"
              >
                #{{ policy.category }}
              </span>
            </div>
          </section>

          <!-- CTA -->
          <div class="flex flex-col sm:flex-row gap-4 sm:gap-6 pt-8 border-t-2 border-gray-100">
            <a
              :href="detailLink || undefined"
              :target="detailLink ? '_blank' : undefined"
              :rel="detailLink ? 'noopener noreferrer' : undefined"
              :aria-disabled="!detailLink"
              @click="handleDetailClick"
              class="flex-1 bg-gradient-to-r from-blue-500 to-cyan-500 text-white px-10 py-5 rounded-2xl hover:shadow-2xl transition-all flex items-center justify-center gap-3 text-lg shadow-lg text-center"
              :class="{
                'opacity-60 cursor-not-allowed hover:shadow-none pointer-events-none': !detailLink,
                'cursor-pointer': !!detailLink,
              }"
            >
              <ExternalLink :size="24" />
              <span>관련 페이지로 이동</span>
            </a>
            <button
              type="button"
              class="px-10 py-5 border-2 border-blue-500 text-blue-600 rounded-2xl hover:bg-blue-50 transition-all text-lg cursor-pointer"
              @click="handleShare"
            >
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
const detailLink = computed(() => {
  const p = policy.value;
  if (!p) return '';
  const rawLink =
    p.detailLink ||
    p.raw?.detail_link ||
    (Array.isArray(p.raw?.detail_links) && p.raw.detail_links[0]) ||
    '';
  const trimmed = rawLink.toString().trim();
  if (!trimmed) return '';
  if (/^https?:\/\//i.test(trimmed)) return trimmed;
  return `https://${trimmed}`;
});

const displayBenefits = computed(() => policy.value?.benefits || '');

const groupedEligibility = computed(() => {
  const items = policy.value?.eligibility || [];
  const map = new Map();

  items.forEach((raw) => {
    const text = (raw || '').toString();
    let label = '';
    let value = '';

    if (text.includes('|')) {
      const [l, v] = text.split('|');
      label = l.trim();
      value = (v || '').replace(/^:?\s*/, '').trim() || '제한없음';
    } else if (text.includes(':')) {
      const [l, ...rest] = text.split(':');
      label = l.trim();
      value = rest.join(':').trim() || '제한없음';
    } else {
      label = '기타';
      value = text.trim();
    }

    if (!label) return;
    const prev = map.get(label) || [];
    if (value && !prev.includes(value)) {
      prev.push(value);
    }
    map.set(label, prev);
  });

  return Array.from(map.entries()).map(([label, values]) => ({
    label,
    values: values.filter(Boolean),
  }));
});

const formatEligibility = (group) => {
  const vals = (group?.values || []).filter(Boolean);
  if (!vals.length) return '제한없음';
  return vals.join('\n');
};

const handleDetailClick = (event) => {
  if (!detailLink.value) {
    event.preventDefault();
    return;
  }
  event.preventDefault();
  window.open(detailLink.value, '_blank', 'noopener,noreferrer');
};

const handleShare = async () => {
  if (!policy.value) return;
  const shareUrl = window.location.href;
  const title = policy.value.title || '정책 정보';
  const text = policy.value.description || '';

  try {
    if (navigator.share) {
      await navigator.share({ title, text, url: shareUrl });
      return;
    }

    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(shareUrl);
      alert('링크를 복사했습니다.');
      return;
    }

    const textarea = document.createElement('textarea');
    textarea.value = shareUrl;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
    alert('링크를 복사했습니다.');
  } catch (error) {
    console.error('공유에 실패했습니다:', error);
    alert('공유 중 문제가 발생했습니다.');
  }
};

onMounted(() => {
  if (!policy.value) {
    policyStore.loadPolicyById(policyId.value);
  }
});
</script>
