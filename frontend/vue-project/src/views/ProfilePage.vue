<template>
  <div class="min-h-screen">
    <div class="max-w-[1000px] mx-auto px-8 lg:px-12 py-12">
      <div class="mb-12">
        <h1 class="text-blue-900 mb-3 text-4xl">내 프로필</h1>
        <p class="text-gray-600 text-lg">
          프로필을 채우면 더 정확한 정책 추천을 받을 수 있습니다.
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
                {{ userStore.isProfileComplete ? '모든 정보가 입력되었습니다.' : '추가 정보를 입력해주세요.' }}
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
          <!-- Name -->
          <div>
            <label class="block text-gray-700 mb-3 text-lg">
              이름 <span class="text-red-500">*</span>
            </label>
            <input
              type="text"
              v-model="formData.name"
              class="w-full px-5 py-4 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
              placeholder="홍길동"
              required
            />
          </div>

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
              max="40"
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
              <option value="">선택해주세요</option>
              <option v-for="region in regionOptions" :key="region" :value="region">{{ region }}</option>
            </select>
          </div>

          <!-- Employment Status -->
          <div>
            <label class="block text-gray-700 mb-3 text-lg">
              취업 상태 <span class="text-red-500">*</span>
            </label>
            <select
              v-model="formData.employmentStatus"
              class="w-full px-5 py-4 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
              required
            >
              <option value="">선택해주세요</option>
              <option value="취업">취업</option>
              <option value="미취업">미취업</option>
              <option value="학생">학생</option>
              <option value="자영업">자영업</option>
            </select>
          </div>

          <!-- Education -->
          <div>
            <label class="block text-gray-700 mb-3 text-lg">
              학력 <span class="text-red-500">*</span>
            </label>
            <select
              v-model="formData.education"
              class="w-full px-5 py-4 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
              required
            >
              <option value="">선택해주세요</option>
              <option value="고등학교 졸업">고등학교 졸업</option>
              <option value="대학교 재학">대학교 재학</option>
              <option value="대학교 졸업">대학교 졸업</option>
              <option value="대학원 재학">대학원 재학</option>
              <option value="대학원 졸업">대학원 졸업</option>
            </select>
          </div>

          <!-- Income -->
          <div>
            <label class="block text-gray-700 mb-3 text-lg">
              소득 구간 <span class="text-red-500">*</span>
            </label>
            <select
              v-model="formData.income"
              class="w-full px-5 py-4 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
              required
            >
              <option value="">선택해주세요</option>
              <option value="1000만원 미만">1000만원 미만</option>
              <option value="1000-2000만원">1000-2000만원</option>
              <option value="2000-3000만원">2000-3000만원</option>
              <option value="3000-4000만원">3000-4000만원</option>
              <option value="4000-5000만원">4000-5000만원</option>
              <option value="5000만원 이상">5000만원 이상</option>
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
          <p v-if="formData.interests.length === 0" class="text-red-500 mt-3 text-sm">최소 1개 이상 선택해주세요</p>
        </div>

        <!-- Submit Button -->
        <div class="flex gap-6">
          <button
            type="submit"
            class="flex-1 bg-gradient-to-r from-blue-500 to-cyan-500 text-white px-10 py-5 rounded-2xl hover:shadow-2xl transition-all flex items-center justify-center gap-3 text-lg shadow-lg"
          >
            <Save :size="24" />
            <span>저장하기</span>
          </button>
        </div>

        <!-- Success / Error Message -->
        <div v-if="message" :class="['mt-6 rounded-2xl p-6 flex items-center gap-4', messageType === 'success' ? 'bg-green-50 border-2 border-green-200 text-green-700' : 'bg-red-50 border-2 border-red-200 text-red-700']">
          <div class="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0" :class="messageType === 'success' ? 'bg-green-500' : 'bg-red-500'">
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
const formData = ref({ ...userStore.profile });
const message = ref('');
const messageType = ref('success');

const interestOptions = ['창업', '주거', '교육', '취업', '문화', '건강', '지역', '농업'];
const regionOptions = ['서울', '경기', '인천', '부산', '대구', '광주', '대전', '울산', '세종', '강원', '충북', '충남', '전북', '전남', '경북', '경남', '제주', '비수도권', '전국'];

onMounted(async () => {
  await userStore.loadProfile();
  formData.value = { ...userStore.profile };
});

watch(
  () => userStore.profile,
  (newProfile) => {
    formData.value = { ...newProfile };
  },
  { deep: true }
);

const completionPercentage = computed(() => {
  const values = Object.values(formData.value);
  const completed = values.filter((v) => (Array.isArray(v) ? v.length > 0 : v !== '')).length;
  return Math.round((completed / values.length) * 100);
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
    message.value = '프로필이 성공적으로 저장되었습니다.';
    messageType.value = 'success';
  } else {
    message.value = userStore.error || '프로필 저장에 실패했습니다.';
    messageType.value = 'error';
  }
  setTimeout(() => {
    message.value = '';
  }, 3000);
};
</script>
