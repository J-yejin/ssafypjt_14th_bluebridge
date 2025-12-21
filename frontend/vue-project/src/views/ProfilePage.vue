<template>
  <div class="min-h-screen">
    <div class="max-w-[800px] mx-auto px-8 lg:px-12 py-12">
      <div class="mb-12 text-center">
        <h1 class="text-blue-900 mb-3 text-4xl">마이 프로필</h1>
        <p class="text-gray-600 text-lg">
          프로필을 채우면 맞춤 정책 추천과 알림을 받을 수 있습니다.
        </p>
      </div>

      <!-- Profile Completion Status -->
      <div class="bg-white rounded-2xl shadow-lg p-8 mb-8 border border-blue-100">
        <div class="flex items-center justify-between mb-4">
          <div class="flex items-center gap-3">
            <div :class="['w-12 h-12 rounded-xl flex items-center justify-center', userStore.isProfileComplete ? 'bg-green-500' : 'bg-blue-500']">
              <User :size="24" class="text-white" />
            </div>
            <div>
              <span class="text-gray-700 text-lg block">프로필 완성도</span>
              <span :class="[userStore.isProfileComplete ? 'text-green-600' : 'text-blue-600', 'text-sm']">
                {{ userStore.isProfileComplete ? '모든 필수 항목이 채워졌습니다.' : '필수 정보를 입력해 주세요.' }}
              </span>
            </div>
          </div>
          <span :class="['text-2xl', userStore.isProfileComplete ? 'text-green-600' : 'text-blue-600']">
            {{ completionPercentage }}%
          </span>
        </div>
        <div class="w-full bg-gray-200 rounded-full h-4">
          <div
            :class="[
              'h-4 rounded-full transition-all',
              userStore.isProfileComplete ? 'bg-gradient-to-r from-green-500 to-green-600' : 'bg-gradient-to-r from-blue-500 to-cyan-500'
            ]"
            :style="{ width: completionPercentage + '%' }"
          />
        </div>
      </div>

      <!-- Profile Form -->
      <form @submit.prevent="handleSubmit" class="bg-white rounded-2xl shadow-lg p-10 border border-blue-100">
        <div class="grid md:grid-cols-2 gap-8 mb-10">
          <!-- Age -->
          <div>
            <label class="block text-gray-700 mb-3 text-lg">
              나이 <span class="text-red-500">*</span>
            </label>
            <input
              type="number"
              v-model="formData.age"
              class="w-full px-5 py-4 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
              placeholder="25"
              min="18"
              max="99"
              required
            />
          </div>

          <!-- Region -->
          <div>
            <label class="block text-gray-700 mb-3 text-lg">
              거주 지역 <span class="text-red-500">*</span>
            </label>
            <select
              v-model="formData.region"
              class="w-full px-5 py-4 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
              required
            >
              <option value="">선택해 주세요</option>
              <option v-for="region in regionOptions" :key="region" :value="region">{{ region }}</option>
            </select>
          </div>
        </div>

        <!-- Interests -->
        <div class="mb-10 p-8 bg-gradient-to-br from-blue-50 to-cyan-50 rounded-2xl border border-blue-100">
          <label class="block text-gray-700 mb-4 text-lg">
            관심 분야 <span class="text-red-500">*</span>
            <span class="text-gray-500 ml-3">(중복 선택 가능)</span>
          </label>
          <div class="flex flex-wrap gap-4">
            <button
              v-for="interest in interestOptions"
              :key="interest"
              type="button"
              @click="toggleInterest(interest)"
              :class="[
                'px-6 py-3 rounded-xl transition-all text-lg',
                formData.interests.includes(interest)
                  ? 'bg-blue-500 text-white shadow-md scale-105'
                  : 'bg-white text-gray-700 hover:bg-gray-50 border-2 border-gray-200'
              ]"
            >
              {{ interest }}
            </button>
          </div>
          <p v-if="formData.interests.length === 0" class="text-red-500 mt-3 text-sm">최소 1개 이상 선택해 주세요</p>
        </div>

        <!-- Submit Button -->
        <div class="flex gap-6">
          <button
            type="submit"
            class="flex-1 bg-gradient-to-r from-blue-500 to-cyan-500 text-white px-10 py-5 rounded-2xl hover:shadow-2xl transition-all flex items-center justify-center gap-3 text-lg shadow-lg"
          >
            <Save :size="24" />
            <span>{{ userStore.isProfileComplete ? '수정하기' : '저장하기' }}</span>
          </button>
        </div>

        <!-- Success / Error Message -->
        <div
          v-if="message"
          :class="[
            'mt-6 rounded-2xl p-6 flex items-center gap-4',
            messageType === 'success'
              ? 'bg-green-50 border-2 border-green-200 text-green-700'
              : 'bg-red-50 border-2 border-red-200 text-red-700'
          ]"
        >
          <div
            class="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0"
            :class="messageType === 'success' ? 'bg-green-500' : 'bg-red-500'"
          >
            <CheckCircle2 :size="24" class="text-white" />
          </div>
          <span class="text-lg">{{ message }}</span>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { User, Save, CheckCircle2 } from 'lucide-vue-next';
import { useUserStore } from '../stores/userStore';

const userStore = useUserStore();

const cloneProfile = (profile) => {
  const base = {
    age: '',
    region: '',
    interests: [],
  };
  return { ...base, ...(profile || {}), interests: [...(profile?.interests || base.interests)] };
};

const formData = ref(cloneProfile(userStore.profile));
const message = ref('');
const messageType = ref('success');

const interestOptions = ['취업', '주거', '교육', '취업지원', '문화', '건강', '지역', '창업'];
const regionOptions = ['서울', '경기', '인천', '부산', '대구', '광주', '대전', '울산', '세종', '강원', '충북', '충남', '전북', '전남', '경북', '경남', '제주', '비수도권', '전국'];

onMounted(async () => {
  await userStore.loadProfile();
  formData.value = cloneProfile(userStore.profile);
});

watch(
  () => userStore.profile,
  (newProfile) => {
    formData.value = cloneProfile(newProfile);
  },
  { deep: false }
);

const completionPercentage = computed(() => {
  const requiredFields = ['age', 'region', 'interests'];
  const total = requiredFields.length;
  const filled = requiredFields.filter((k) => {
    const val = formData.value[k];
    if (Array.isArray(val)) return val.length > 0;
    return val !== null && val !== undefined && val !== '';
  }).length;
  return Math.round((filled / total) * 100);
});

const toggleInterest = (interest) => {
  const index = formData.value.interests.indexOf(interest);
  if (index > -1) {
    formData.value.interests.splice(index, 1);
  } else {
    formData.value.interests.push(interest);
  }
};

const handleSubmit = async () => {
  userStore.updateProfile(formData.value);
  const ok = await userStore.saveProfile();
  if (ok) {
    message.value = '프로필이 저장되었습니다.';
    messageType.value = 'success';
    await userStore.loadProfile();
    formData.value = cloneProfile(userStore.profile);
  } else {
    message.value = userStore.error || '프로필 저장에 실패했습니다.';
    messageType.value = 'error';
  }
  setTimeout(() => {
    message.value = '';
  }, 3000);
};
</script>

<style scoped>
:global(body) {
  background: #f6f8fb;
}
</style>
