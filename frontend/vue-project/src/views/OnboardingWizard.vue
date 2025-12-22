<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-sky-50 to-white px-4 py-12">
    <div class="w-full max-w-2xl bg-white rounded-3xl shadow-2xl border border-blue-100 p-8 md:p-12">
      <div class="text-center mb-6">
        <p class="text-sm text-gray-500 font-medium">{{ currentIndex + 1 }} / {{ steps.length }}</p>
        <h1 class="text-2xl md:text-3xl font-semibold text-blue-900 mt-2">{{ currentStep.title }}</h1>
        <p v-if="currentStep.caption" class="text-gray-500 mt-2 text-sm">{{ currentStep.caption }}</p>
      </div>

      <div class="space-y-4">
        <!-- 단일 선택 -->
        <div v-if="currentStep.type === 'choice'" class="space-y-3">
          <button
            v-for="option in currentStep.options"
            :key="option.value"
            type="button"
            @click="handleChoice(option.value)"
            :class="[
              'w-full py-3 px-4 rounded-xl border transition-all',
              formData[currentStep.key] === option.value
                ? 'border-blue-500 bg-blue-50 text-blue-700 shadow-sm'
                : 'border-gray-200 bg-white text-gray-700 hover:bg-gray-50'
            ]"
          >
            {{ option.label }}
          </button>
        </div>

        <!-- 숫자/텍스트 입력 -->
        <div v-else-if="currentStep.type === 'input'" class="space-y-2">
          <input
            :type="currentStep.inputType || 'text'"
            v-model="formData[currentStep.key]"
            :placeholder="currentStep.placeholder"
            :min="currentStep.min"
            :max="currentStep.max"
            class="w-full py-3 px-4 rounded-xl border-2 border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <!-- 단일 셀렉트 -->
        <div v-else-if="currentStep.type === 'select'" class="space-y-2">
          <select
            v-model="formData[currentStep.key]"
            class="w-full py-3 px-4 rounded-xl border-2 border-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">{{ currentStep.placeholder || '선택해 주세요' }}</option>
            <option v-for="option in currentStep.options" :key="option.value || option" :value="option.value || option">
              {{ option.label || option }}
            </option>
          </select>
        </div>

        <!-- 다중 선택 -->
        <div v-else-if="currentStep.type === 'multi'" class="space-y-3">
          <div class="flex flex-wrap gap-2">
            <button
              v-if="currentStep.allowNone"
              type="button"
              @click="clearMulti(currentStep.key)"
              :class="[
                'px-3 py-2 rounded-xl text-sm border transition-all',
                formData[currentStep.key].length === 0
                  ? 'border-blue-500 bg-blue-50 text-blue-700'
                  : 'border-gray-200 bg-white text-gray-700 hover:bg-gray-50'
              ]"
            >
              해당 없음
            </button>
            <button
              v-for="option in currentStep.options"
              :key="option"
              type="button"
              @click="toggleMulti(currentStep.key, option)"
              :class="[
                'px-3 py-2 rounded-xl text-sm border transition-all',
                formData[currentStep.key].includes(option)
                  ? 'border-blue-500 bg-blue-50 text-blue-700'
                  : 'border-gray-200 bg-white text-gray-700 hover:bg-gray-50'
              ]"
            >
              {{ option }}
            </button>
          </div>
          <p v-if="currentStep.required && formData[currentStep.key].length === 0" class="text-red-500 text-sm">
            최소 1개 이상 선택해 주세요.
          </p>
        </div>
      </div>

      <div class="mt-8 flex items-center justify-between">
        <button
          type="button"
          @click="prevStep"
          :disabled="currentIndex === 0"
          class="px-5 py-3 rounded-xl border border-gray-200 text-gray-600 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          이전
        </button>
        <button
          type="button"
          @click="nextStep"
          :disabled="!canProceed"
          class="px-6 py-3 rounded-xl bg-gradient-to-r from-blue-500 to-cyan-500 text-white shadow-md hover:shadow-lg transition disabled:opacity-40 disabled:cursor-not-allowed"
        >
          {{ isLastStep ? '완료' : '다음' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '../stores/userStore';
import { useAuthStore } from '../stores/authStore';

const userStore = useUserStore();
const authStore = useAuthStore();
const router = useRouter();

const interestOptions = ['취업', '주거', '교육', '문화', '건강', '지역', '창업'];
const regionOptions = ['서울', '경기', '인천', '부산', '대구', '광주', '대전', '울산', '세종', '강원', '충북', '충남', '전북', '전남', '경북', '경남', '제주', '기타'];
const specialTargetOptions = ['국가유공자', '장애인', '보훈가족', '한부모', '저소득층', '다자녀', '군인·전역예정', '농어업인'];
const employmentOptions = [
  { label: '미취업', value: 'unemployed' },
  { label: '재직자', value: 'employed' },
  { label: '학생', value: 'student' },
  { label: '창업/자영업', value: 'self_employed' },
  { label: '선택안함', value: '' },
];
const educationOptions = [
  { label: '고졸 이하', value: 'highschool' },
  { label: '전문대', value: 'college' },
  { label: '대학교', value: 'university' },
  { label: '대학원 이상', value: 'graduate' },
  { label: '선택안함', value: '' },
];

const steps = [
  {
    key: 'gender',
    title: '성별이 어떻게 되세요?',
    type: 'choice',
    options: [
      { label: '남성', value: 'male' },
      { label: '여성', value: 'female' },
      { label: '선택안함', value: '' },
    ],
    required: false,
  },
  {
    key: 'age',
    title: '나이가 어떻게 되세요?',
    type: 'input',
    inputType: 'number',
    placeholder: '예) 25',
    min: 18,
    max: 99,
    required: true,
  },
  {
    key: 'region',
    title: '거주 지역은 어디인가요?',
    type: 'select',
    options: regionOptions,
    placeholder: '거주 지역을 선택해 주세요',
    required: true,
  },
  {
    key: 'employmentStatus',
    title: '현재 취업 상태를 알려주세요.',
    type: 'select',
    options: employmentOptions,
    required: false,
  },
  {
    key: 'educationLevel',
    title: '최종 학력을 선택해 주세요.',
    type: 'select',
    options: educationOptions,
    required: false,
  },
  {
    key: 'interests',
    title: '관심 분야를 선택해 주세요.',
    type: 'multi',
    options: interestOptions,
    required: true,
    allowNone: false,
  },
  {
    key: 'specialTargets',
    title: '지원대상에 해당하나요?',
    type: 'multi',
    options: specialTargetOptions,
    required: false,
    allowNone: true,
  },
];

const formData = ref({
  gender: '',
  age: '',
  region: '',
  employmentStatus: '',
  educationLevel: '',
  interests: [],
  specialTargets: [],
});

const currentIndex = ref(0);
const currentStep = computed(() => steps[currentIndex.value]);
const isLastStep = computed(() => currentIndex.value === steps.length - 1);

const canProceed = computed(() => {
  const step = currentStep.value;
  const value = formData.value[step.key];
  if (step.type === 'multi') {
    return step.required ? Array.isArray(value) && value.length > 0 : true;
  }
  if (step.required) {
    return value !== null && value !== undefined && value !== '';
  }
  return true;
});

const nextStep = async () => {
  if (isLastStep.value) {
    await saveAndFinish();
    return;
  }
  currentIndex.value += 1;
};

const prevStep = () => {
  if (currentIndex.value === 0) return;
  currentIndex.value -= 1;
};

const handleChoice = (value) => {
  formData.value[currentStep.value.key] = value;
};

const toggleMulti = (key, option) => {
  const list = formData.value[key] || [];
  const idx = list.indexOf(option);
  if (idx > -1) {
    list.splice(idx, 1);
  } else {
    list.push(option);
  }
  formData.value[key] = [...list];
};

const clearMulti = (key) => {
  formData.value[key] = [];
};

const saveAndFinish = async () => {
  userStore.updateProfile({
    gender: formData.value.gender,
    age: formData.value.age,
    region: formData.value.region,
    employmentStatus: formData.value.employmentStatus,
    educationLevel: formData.value.educationLevel,
    interests: formData.value.interests,
    specialTargets: formData.value.specialTargets,
  });
  await userStore.saveProfile();
  router.push('/recommend');
};

onMounted(async () => {
  // 로그인 안 되어 있으면 로그인 페이지로
  if (!authStore.isAuthenticated) {
    router.push('/login');
    return;
  }
  await userStore.loadProfile();
  formData.value = {
    gender: userStore.profile.gender || '',
    age: userStore.profile.age || '',
    region: userStore.profile.region || '',
    employmentStatus: userStore.profile.employmentStatus || '',
    educationLevel: userStore.profile.educationLevel || '',
    interests: [...(userStore.profile.interests || [])],
    specialTargets: [...(userStore.profile.specialTargets || [])],
  };
});
</script>

<style scoped>
button {
  font-weight: 600;
}
</style>
