<template>
  <div class="min-h-screen">
    <div class="max-w-[900px] mx-auto px-8 lg:px-12 py-12">
      <div class="mb-12 text-center">
        <h1 class="text-blue-900 mb-3 text-4xl">마이 페이지</h1>
        <p class="text-gray-600 text-lg">
          프로필을 채우면 맞춤 정책 추천과 안내를 받을 수 있어요.
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
                {{ userStore.isProfileComplete ? '모든 필수 항목을 입력했어요!' : '필수 정보를 입력해 주세요.' }}
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
              ,
              completionPercentage === 100 ? 'completion-animate' : ''
            ]"
            :style="{ width: completionPercentage + '%' }"
          />
        </div>
      </div>

      <!-- Profile Form -->
      <form @submit.prevent="handleSubmit" class="bg-white rounded-2xl shadow-lg p-10 border border-blue-100 space-y-3">
        <!-- Interests -->
        <div class="p-8 bg-gradient-to-br from-blue-50 to-cyan-50 rounded-2xl border border-blue-100">
          <label class="block text-gray-700 mb-3 text-lg">
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
          <p v-if="formData.interests.length === 0" class="text-red-500 mt-3 text-sm">최소 1개 이상 선택해 주세요.</p>
        </div>

        <!-- Special targets -->
        <div class="p-8 bg-gradient-to-br from-blue-50 to-cyan-50 rounded-2xl border border-blue-100">
          <label class="block text-gray-700 mb-3 text-lg">
            지원대상 <span class="text-red-500">*</span>
            <span class="text-gray-500 ml-3">(중복 선택 가능)</span>
          </label>
          <div class="flex flex-wrap gap-4">
            <button
              type="button"
              @click="clearSpecialTargets"
              :class="[
                'px-6 py-3 rounded-xl transition-all text-lg',
                formData.specialTargets.includes(noneSpecialTarget)
                  ? 'bg-blue-500 text-white shadow-md scale-105'
                  : 'bg-white text-gray-700 hover:bg-gray-50 border-2 border-gray-200'
              ]"
            >
              해당 없음
            </button>
            <button
              v-for="target in specialTargetOptions"
              :key="target"
              type="button"
              @click="toggleSpecialTarget(target)"
              :class="[
                'px-6 py-3 rounded-xl transition-all text-lg',
                formData.specialTargets.includes(target)
                  ? 'bg-blue-500 text-white shadow-md scale-105'
                  : 'bg-white text-gray-700 hover:bg-gray-50 border-2 border-gray-200'
              ]"
            >
              {{ target }}
            </button>
          </div>
          <p v-if="formData.specialTargets.length === 0" class="text-red-500 mt-3 text-sm">최소 1개 이상 선택해 주세요.</p>
        </div>

        <div class="grid md:grid-cols-2 gap-x-8 gap-y-0 field-grid">
          <!-- Age -->
          <div>
            <label class="block text-gray-700 text-lg field-label">
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
            <label class="block text-gray-700 text-lg field-label">
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

          <div>
            <label class="block text-gray-700 text-lg field-label">
              성별 <span class="text-red-500">*</span>
            </label>
            <select
              v-model="formData.gender"
              class="w-full px-5 py-4 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
              required
            >
              <option value="">선택해 주세요</option>
              <option value="male">남성</option>
              <option value="female">여성</option>
              <option value="other">기타/응답안함</option>
            </select>
          </div>
          <div>
            <label class="block text-gray-700 text-lg field-label">
              취업 상태 <span class="text-red-500">*</span>
            </label>
            <select
              v-model="formData.employmentStatus"
              class="w-full px-5 py-4 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
              required
            >
              <option value="">선택해 주세요</option>
              <option v-for="opt in employmentOptions" :key="opt.value" :value="opt.value">
                {{ opt.label }}
              </option>
            </select>
          </div>

          <div>
            <label class="block text-gray-700 text-lg field-label">
              학력 <span class="text-red-500">*</span>
            </label>
            <select
              v-model="formData.educationLevel"
              class="w-full px-5 py-4 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
              required
            >
              <option value="">선택해 주세요</option>
              <option v-for="opt in educationOptions" :key="opt.value" :value="opt.value">
                {{ opt.label }}
              </option>
            </select>
          </div>
          <div>
            <label class="block text-gray-700 text-lg field-label">
              전공 <span class="text-red-500">*</span>
            </label>
            <input
              type="text"
              v-model="formData.major"
              class="w-full px-5 py-4 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
              placeholder="예) 컴퓨터공학"
              required
            />
          </div>

          <div>
            <label class="block text-gray-700 text-lg field-label">
              월 소득(만 원) <span class="text-gray-500 text-sm">(선택)</span>
            </label>
            <input
              type="number"
              v-model="formData.householdIncome"
              class="w-full px-5 py-4 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
              placeholder="예) 3500000 (모르면 비워두시면 됩니다.)"
              min="0"
            />
          </div>
          <div>
            <label class="block text-gray-700 text-lg field-label">
              가구원 수 <span class="text-gray-500 text-sm">(선택)</span>
            </label>
            <input
              type="number"
              v-model="formData.familySize"
              class="w-full px-5 py-4 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
              placeholder="예) 4"
              min="1"
              max="10"
            />
          </div>

          <div class="md:col-span-2">
            <label class="block text-gray-700 text-lg field-label">
              소득분위 (자동 계산)
              <span class="text-gray-500 text-sm ml-2">입력한 값으로 소득분위가 자동 계산 됩니다.</span>
            </label>
            <input
              type="text"
              :value="formData.incomeQuintile || '소득/가구원 수를 입력하면 계산됩니다.'"
              class="w-full px-5 py-4 border-2 border-gray-200 rounded-xl bg-gray-50 text-gray-600"
              readonly
            />
          </div>
        </div>

        <!-- Submit Button -->
        <div class="flex gap-6 mt-6">
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

      <!-- 게시글 관리 -->
      <div class="bg-white rounded-2xl shadow-lg p-10 border border-blue-100 space-y-4 mt-8">
        <div class="flex items-center justify-between">
          <div>
            <h2 class="text-2xl font-semibold text-blue-900">게시글 관리</h2>
            <p class="text-gray-600 mt-1">내가 작성한 게시글을 확인하고 관리할 수 있습니다.</p>
          </div>
          <router-link
            v-if="authStore.isAuthenticated"
            to="/boards/new"
            class="px-4 py-2 rounded-xl bg-gradient-to-r from-blue-500 to-cyan-500 text-white shadow hover:shadow-lg transition"
          >
            글 작성
          </router-link>
        </div>

        <div v-if="myBoards.length === 0" class="text-gray-500 bg-gray-50 border border-gray-100 rounded-xl p-6">
          작성한 게시글이 없습니다.
        </div>
        <ul v-else class="space-y-3">
          <li
            v-for="board in myBoards"
            :key="board.id"
            class="flex flex-col md:flex-row md:items-center md:justify-between gap-2 border border-gray-100 rounded-xl p-4 hover:bg-gray-50 transition"
          >
            <div class="space-y-1">
              <div class="flex items-center gap-2">
                <router-link :to="`/boards/${board.id}`" class="text-lg font-semibold text-blue-900 hover:underline">
                  {{ board.title }}
                </router-link>
                <span class="px-3 py-1 text-sm rounded-full bg-green-50 text-green-700 border border-green-200">
                  {{ displayCategory(board.category) }}
                </span>
              </div>
              <p class="text-gray-500 text-sm">작성일 {{ formatDate(board.created_at) }}</p>
            </div>
            <div class="flex gap-2">
              <router-link
                :to="`/boards/${board.id}`"
                class="px-3 py-2 rounded-lg border border-gray-200 text-gray-700 hover:bg-gray-100 transition"
              >
                상세보기
              </router-link>
              <button
                type="button"
                class="px-3 py-2 rounded-lg border border-red-200 text-red-600 hover:bg-red-50 transition"
                @click="handleDeleteBoard(board.id)"
              >
                삭제
              </button>
            </div>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue';
import { User, Save, CheckCircle2 } from 'lucide-vue-next';
import { useUserStore } from '../stores/userStore';
import { useBoardStore } from '../stores/boardStore';
import { useAuthStore } from '../stores/authStore';

const userStore = useUserStore();
const boardStore = useBoardStore();
const authStore = useAuthStore();
const noneSpecialTarget = 'none';

const cloneProfile = (profile) => {
  const base = {
    age: '',
    region: '',
    interests: [],
    gender: '',
    householdIncome: '',
    familySize: '',
    incomeQuintile: '',
    employmentStatus: '',
    educationLevel: '',
    major: '',
    specialTargets: [],
  };
  return {
    ...base,
    ...(profile || {}),
    interests: [...(profile?.interests || base.interests)],
    specialTargets: [...(profile?.specialTargets || base.specialTargets)],
  };
};

const formData = ref(cloneProfile(userStore.profile));
const message = ref('');
const messageType = ref('success');

const interestOptions = ['취업', '주거', '교육', '문화', '건강', '지역', '창업'];
const regionOptions = ['서울', '경기', '인천', '부산', '대구', '광주', '대전', '울산', '세종', '강원', '충북', '충남', '전북', '전남', '경북', '경남', '제주', '기타'];
const employmentOptions = [
  { label: '미취업', value: 'unemployed' },
  { label: '재직자', value: 'employed' },
  { label: '학생', value: 'student' },
  { label: '창업/자영업', value: 'self_employed' },
];
const educationOptions = [
  { label: '고졸 이하', value: 'highschool' },
  { label: '전문대', value: 'college' },
  { label: '대학교', value: 'university' },
  { label: '대학원 이상', value: 'graduate' },
];
const specialTargetOptions = ['국가유공자', '장애인', '보훈가족', '한부모', '저소득층', '다자녀', '군인·전역예정', '농어업인'];

onMounted(async () => {
  await userStore.loadProfile();
  formData.value = cloneProfile(userStore.profile);
  await boardStore.loadBoards();
});

watch(
  () => userStore.profile,
  (newProfile) => {
    formData.value = cloneProfile(newProfile);
  },
  { deep: false }
);

const completionPercentage = computed(() => {
  const requiredFields = ['age', 'region', 'interests', 'gender', 'employmentStatus', 'educationLevel', 'major', 'specialTargets'];
  const total = requiredFields.length;
  const filled = requiredFields.filter((k) => {
    const val = formData.value[k];
    if (Array.isArray(val)) return val.length > 0;
    return val !== null && val !== undefined && val !== '';
  }).length;
  return Math.round((filled / total) * 100);
});

const myBoards = computed(() => {
  const me = authStore.username;
  if (!me) return [];
  return (boardStore.boards || []).filter((b) => b.user === me);
});

const handleDeleteBoard = async (id) => {
  if (!window.confirm('해당 게시글을 삭제하시겠습니까?')) return;
  try {
    await boardStore.removeBoard(id);
    await boardStore.loadBoards();
  } catch (err) {
    alert(err?.message || '게시글 삭제에 실패했습니다.');
  }
};

const formatDate = (value) => {
  if (!value) return '';
  return new Date(value).toLocaleDateString();
};

const displayCategory = (value) => {
  const map = {
    notice: '공지사항',
    review: '자료실',
    free: '자유게시판',
    question: '자유게시판',
  };
  return map[value] || '기타';
};

const toggleInterest = (interest) => {
  const index = formData.value.interests.indexOf(interest);
  if (index > -1) {
    formData.value.interests.splice(index, 1);
  } else {
    formData.value.interests.push(interest);
  }
};

const toggleSpecialTarget = (target) => {
  const index = formData.value.specialTargets.indexOf(target);
  if (index > -1) {
    formData.value.specialTargets.splice(index, 1);
  } else {
    formData.value.specialTargets = formData.value.specialTargets.filter((item) => item !== noneSpecialTarget);
    formData.value.specialTargets.push(target);
  }
};

const clearSpecialTargets = () => {
  if (formData.value.specialTargets.includes(noneSpecialTarget)) {
    formData.value.specialTargets = [];
    return;
  }
  formData.value.specialTargets = [noneSpecialTarget];
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
  background: #f5fbf1;
}

.field-grid {
  row-gap: 0.75rem;
}

.field-label {
  margin-bottom: 0.75rem;
}

.completion-animate {
  animation: completionFill 900ms ease-out 1, completionPulseBig 900ms ease-out 1;
  animation-delay: 0ms, 900ms;
  transform-origin: center;
}

@keyframes completionFill {
  0% {
    width: 0%;
  }
  100% {
    width: 100%;
  }
}

@keyframes completionPulseBig {
  0% {
    box-shadow: 0 0 0 0 rgba(34, 197, 94, 0.6);
    transform: scaleY(1);
  }
  60% {
    box-shadow: 0 0 0 14px rgba(34, 197, 94, 0);
    transform: scaleY(1.14);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(34, 197, 94, 0);
    transform: scaleY(1);
  }
}
</style>
