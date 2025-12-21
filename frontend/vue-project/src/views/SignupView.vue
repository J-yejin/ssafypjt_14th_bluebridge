<template>
  <div class="auth-wrap">
    <div class="card">
      <h1>회원가입</h1>
      <p class="lead">아이디와 비밀번호를 입력해 계정을 생성하세요.</p>
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
import { signup } from '../api/client';

const username = ref('');
const password = ref('');
const passwordConfirm = ref('');
const loading = ref(false);
const error = ref('');
const router = useRouter();

const handleSignup = async () => {
  if (password.value !== passwordConfirm.value) {
    error.value = '비밀번호가 일치하지 않습니다';
    return;
  }
  loading.value = true;
  error.value = '';
  try {
    await signup({
      username: username.value,
      password: password.value,
      password_confirm: passwordConfirm.value,
    });
    router.push('/login');
  } catch (e) {
    error.value = e.message || '회원가입에 실패했습니다';
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
  max-width: 420px;
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
input {
  padding: 12px 14px;
  border: 1px solid #d0d7e2;
  border-radius: 12px;
  outline: none;
}
input:focus {
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
.hint {
  margin-top: 12px;
  color: #475569;
}
.hint a {
  color: #2563eb;
  text-decoration: none;
}
</style>
