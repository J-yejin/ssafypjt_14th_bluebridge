<template>
  <div class="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-sky-50 to-white px-4 py-12">
    <div class="w-full max-w-2xl bg-white rounded-[28px] shadow-2xl border border-blue-100 p-8 md:p-12">
      <div class="text-center mb-8">
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
            :class="['option-button', formData[currentStep.key] === option.value ? 'option-button--active' : '']"
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
            class="input-field"
          />
        </div>

        <!-- 단일 셀렉트 -->
        <div v-else-if="currentStep.type === 'select'" class="space-y-3">
          <div class="space-y-2">
            <button
              v-for="option in currentStep.options"
              :key="option.value || option"
              type="button"
              @click="handleChoice(option.value || option)"
              :class="[
                'option-button',
                formData[currentStep.key] === (option.value || option) ? 'option-button--active' : ''
              ]"
            >
              {{ option.label || option }}
            </button>
          </div>
        </div>

        <!-- 다중 선택 -->
        <div v-else-if="currentStep.type === 'multi'" class="space-y-3">
          <div class="space-y-2">
            <button
              v-if="currentStep.allowNone"
              type="button"
              @click="clearMulti(currentStep.key)"
              :class="['option-button', formData[currentStep.key].length === 0 ? 'option-button--active' : '']"
            >
              해당 없음
            </button>
            <button
              v-for="option in currentStep.options"
              :key="option"
              type="button"
              @click="toggleMulti(currentStep.key, option)"
              :class="[
                'option-button',
                formData[currentStep.key].includes(option) ? 'option-button--active' : ''
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

      <div class="mt-10 flex items-center justify-between">
        <button
          type="button"
          @click="prevStep"
          :disabled="currentIndex === 0"
          class="nav-button nav-button--ghost mt-2"
        >
          이전
        </button>
        <button
          type="button"
          @click="nextStep"
          :disabled="!canProceed"
          class="nav-button nav-button--primary mt-2"
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
    key: 'major',
    title: '전공이 무엇인가요?',
    type: 'input',
    inputType: 'text',
    placeholder: '예) 컴퓨터공학 (선택 입력)',
    required: false,
  },
  {
    key: 'householdIncome',
    title: '월 가구소득은 얼마나 되나요? (단위 : 만원)',
    type: 'input',
    inputType: 'number',
    placeholder: '예) 350 (소득을 알지 못하시면, 건너뛰기 가능합니다.)',
    min: 0,
    required: false,
  },
  {
    key: 'familySize',
    title: '가구원 수는 몇 명인가요?',
    type: 'input',
    inputType: 'number',
    placeholder: '예) 4 ',
    min: 1,
    required: false,
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
  employmentStatus: '',
  educationLevel: '',
  major: '',
  householdIncome: '',
  familySize: '',
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
  const incomeInWon = formData.value.householdIncome
    ? Number(formData.value.householdIncome) * 10000
    : null;
  userStore.updateProfile({
    gender: formData.value.gender || '',
    employmentStatus: formData.value.employmentStatus || '',
    educationLevel: formData.value.educationLevel || '',
    major: formData.value.major || '',
    householdIncome: incomeInWon,
    familySize: formData.value.familySize ? Number(formData.value.familySize) : null,
    specialTargets: formData.value.specialTargets || [],
  });
  await userStore.saveProfile();
  router.push('/recommend');
};

onMounted(async () => {
  if (!authStore.isAuthenticated) {
    router.push('/login');
    return;
  }
  await userStore.loadProfile();
  formData.value = {
    gender: userStore.profile.gender || '',
    employmentStatus: userStore.profile.employmentStatus || '',
    educationLevel: userStore.profile.educationLevel || '',
    major: userStore.profile.major || '',
    householdIncome: userStore.profile.householdIncome
      ? Number(userStore.profile.householdIncome) / 10000
      : '',
    familySize: userStore.profile.familySize || '',
    specialTargets: [...(userStore.profile.specialTargets || [])],
  };
});
</script>

<style scoped>
.option-button {
  width: 100%;
  padding: 14px 16px;
  border-radius: 16px;
  border: 2px solid #e5e7eb;
  background: #ffffff;
  color: #0f172a;
  font-weight: 700;
  transition: all 0.12s ease;
}

.option-button--active {
  border-color: #3b82f6;
  background: linear-gradient(135deg, #e0efff 0%, #f4f8ff 100%);
  color: #1d4ed8;
  box-shadow: 0 8px 20px rgba(59, 130, 246, 0.15);
}

.option-button:hover {
  border-color: #bfdbfe;
  background: #f8fbff;
}

.option-button + .option-button {
  margin-top: 10px;
}

.input-field {
  width: 100%;
  padding: 14px 16px;
  border-radius: 16px;
  border: 1.5px solid #e5e7eb;
  background: #ffffff;
  transition: all 0.12s ease;
}

.input-field:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
}

.nav-button {
  padding: 12px 22px;
  border-radius: 14px;
  font-weight: 700;
  transition: all 0.12s ease;
}

.nav-button--ghost {
  border: 1px solid #e5e7eb;
  color: #334155;
  background: #fff;
}

.nav-button--primary {
  background: linear-gradient(135deg, #0ea5e9 0%, #3b82f6 100%);
  color: #fff;
  box-shadow: 0 10px 25px rgba(14, 165, 233, 0.25);
}

.nav-button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  box-shadow: none;
}
</style>
