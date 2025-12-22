<template>
  <div class="auth-wrap">
    <div class="card">
      <h1>회원가입</h1>
      <p class="lead">아이디, 비밀번호와 기본 정보를 입력해 주세요.</p>
      <form @submit.prevent="handleSignup" class="form">
        <label>
          아이디
          <input v-model="username" type="text" required placeholder="아이디" />
        </label>
        <label>
          비밀번호
          <input v-model="password" type="password" required placeholder="비밀번호" />
        </label>
        <label>
          비밀번호 확인
          <input v-model="passwordConfirm" type="password" required placeholder="비밀번호 확인" />
        </label>
        <label>
          나이
          <input v-model.number="age" type="number" min="1" max="120" required placeholder="예) 25" />
        </label>
        <label>
          거주 지역
          <select v-model="region" required>
            <option value="">선택해 주세요</option>
            <option v-for="regionOption in regionOptions" :key="regionOption" :value="regionOption">
              {{ regionOption }}
            </option>
          </select>
        </label>
        <div class="field-group">
          <span class="label">관심 분야 (중복 선택 가능)</span>
          <div class="chip-group">
            <button
              v-for="interest in interestOptions"
              :key="interest"
              type="button"
              :class="['chip', selectedInterests.includes(interest) ? 'chip--active' : '']"
              @click="toggleInterest(interest)"
            >
              {{ interest }}
            </button>
          </div>
          <p v-if="selectedInterests.length === 0" class="helper">최소 1개 이상 선택해 주세요.</p>
        </div>
        <button class="btn primary" type="submit" :disabled="loading">회원가입</button>
        <p v-if="error" class="error">{{ error }}</p>
      </form>
      <p class="hint">
        이미 계정이 있으신가요?
        <router-link to="/login">로그인</router-link>
      </p>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { signup, login } from '../api/client';
import { useAuthStore } from '../stores/authStore';

const username = ref('');
const password = ref('');
const passwordConfirm = ref('');
const age = ref('');
const region = ref('');
const selectedInterests = ref([]);
const loading = ref(false);
const error = ref('');
const router = useRouter();
const authStore = useAuthStore();

const interestOptions = ['취업', '주거', '교육', '문화', '건강', '지역', '창업'];

const regionOptions = [
  '서울',
  '경기',
  '인천',
  '부산',
  '대구',
  '광주',
  '대전',
  '울산',
  '세종',
  '강원',
  '충북',
  '충남',
  '전북',
  '전남',
  '경북',
  '경남',
  '제주',
  '기타',
];

const toggleInterest = (interest) => {
  const idx = selectedInterests.value.indexOf(interest);
  if (idx > -1) {
    selectedInterests.value.splice(idx, 1);
  } else {
    selectedInterests.value.push(interest);
  }
};

const handleSignup = async () => {
  if (password.value !== passwordConfirm.value) {
    error.value = '비밀번호가 일치하지 않습니다';
    return;
  }
  if (!age.value || !region.value || selectedInterests.value.length === 0) {
    error.value = '나이, 지역, 관심 분야를 모두 입력해 주세요';
    return;
  }
  loading.value = true;
  error.value = '';
  try {
    await signup({
      username: username.value,
      password: password.value,
      password_confirm: passwordConfirm.value,
      age: age.value,
      region: region.value,
      interest: selectedInterests.value.join(','),
    });
    // 회원가입 후 자동 로그인
    const loginResp = await login({ username: username.value, password: password.value });
    authStore.setTokens({ access: loginResp?.access, refresh: loginResp?.refresh });
    authStore.setUsername(username.value);
    // 기본 이동: 홈으로 이동, 이후 사용자가 원하는 경우 프로필 페이지로 진입
    router.push('/');
  } catch (e) {
    error.value = e.message || '회원가입 중 오류가 발생했습니다';
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
.auth-wrap {
  min-height: 70vh;
  display: grid;
  place-items: center;
  padding: 32px 16px;
}
.card {
  width: 100%;
  max-width: 480px;
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 16px 40px rgba(15, 23, 42, 0.08);
  border: 1px solid #e5e7eb;
  padding: 28px;
  text-align: center;
}
h1 {
  margin: 0 0 8px;
}
.lead {
  margin: 0 0 16px;
  color: #64748b;
}
.form {
  display: grid;
  gap: 12px;
  text-align: left;
}
label {
  display: grid;
  gap: 6px;
  font-weight: 600;
  color: #0f172a;
}
input,
select {
  padding: 12px 14px;
  border: 1px solid #d0d7e2;
  border-radius: 12px;
  outline: none;
}
input:focus,
select:focus {
  border-color: #2563eb;
  box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);
}
.btn {
  border: none;
  cursor: pointer;
  border-radius: 12px;
  font-weight: 700;
  padding: 12px 16px;
  transition: transform 0.12s ease, box-shadow 0.12s ease, background 0.12s ease;
}
.btn.primary {
  background: #0f60ff;
  color: #fff;
  box-shadow: 0 10px 25px rgba(15, 96, 255, 0.35);
}
.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
.error {
  color: #dc2626;
  font-size: 14px;
  margin: 4px 0 0;
}
.field-group {
  display: grid;
  gap: 8px;
}
.label {
  font-weight: 600;
  color: #0f172a;
}
.chip-group {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}
.chip {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  border: 1px solid #d0d7e2;
  background: #f8fafc;
  padding: 10px 14px;
  border-radius: 9999px;
  cursor: pointer;
  transition: all 0.12s ease;
  min-height: 40px;
  min-width: 64px;
}
.chip--active {
  background: #0f60ff;
  color: #fff;
  border-color: #0f60ff;
  box-shadow: 0 10px 25px rgba(15, 96, 255, 0.25);
}
.helper {
  color: #dc2626;
  font-size: 13px;
}
.hint {
  margin-top: 12px;
  color: #475569;
}
.hint a {
  color: #2563eb;
  text-decoration: none;
}
</style>
