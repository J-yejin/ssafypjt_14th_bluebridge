import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { fetchProfile, saveProfile as saveProfileApi } from '../api/client';

const emptyProfile = {
  name: '',
  age: '',
  region: '',
  employmentStatus: '',
  education: '',
  interests: [],
  income: '',
};

export const useUserStore = defineStore('user', () => {
  const profile = ref({ ...emptyProfile });
  const loading = ref(false);
  const error = ref(null);

  const isProfileComplete = computed(() => {
    const current = profile.value;
    return (
      current.name &&
      current.age &&
      current.region &&
      current.employmentStatus &&
      current.education &&
      current.interests.length > 0 &&
      current.income
    );
  });

  const updateProfile = (newProfile) => {
    profile.value = { ...profile.value, ...newProfile };
  };

  const loadProfile = async () => {
    loading.value = true;
    error.value = null;
    try {
      const data = await fetchProfile();
      if (data) {
        profile.value = { ...emptyProfile, ...data };
      }
    } catch (err) {
      error.value = err.message || '프로필을 불러오지 못했습니다.';
    } finally {
      loading.value = false;
    }
  };

  const saveProfile = async () => {
    loading.value = true;
    error.value = null;
    try {
      await saveProfileApi(profile.value);
      return true;
    } catch (err) {
      error.value = err.message || '프로필 저장에 실패했습니다.';
      return false;
    } finally {
      loading.value = false;
    }
  };

  const resetProfile = () => {
    profile.value = { ...emptyProfile };
  };

  return {
    profile,
    loading,
    error,
    isProfileComplete,
    updateProfile,
    loadProfile,
    saveProfile,
    resetProfile,
  };
});
