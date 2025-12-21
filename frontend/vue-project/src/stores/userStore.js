import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { fetchProfile, saveProfile as saveProfileApi } from '../api/client';

// 백엔드 프로필 스키마: age, region, interest(string)
const emptyProfile = {
  age: '',
  region: '',
  interests: [],
};

export const useUserStore = defineStore('user', () => {
  const profile = ref({ ...emptyProfile });
  const loading = ref(false);
  const error = ref(null);

  const isProfileComplete = computed(() => {
    const current = profile.value;
    return current.age && current.region && current.interests.length > 0;
  });

  const updateProfile = (newProfile) => {
    profile.value = {
      ...profile.value,
      ...newProfile,
      interests: [...(newProfile.interests ?? profile.value.interests ?? [])],
    };
  };

  const loadProfile = async () => {
    loading.value = true;
    error.value = null;
    try {
      const data = await fetchProfile();
      if (data) {
        const interests = data.interest ? data.interest.split(',').map((v) => v.trim()).filter(Boolean) : [];
        profile.value = { ...emptyProfile, age: data.age || '', region: data.region || '', interests };
      }
    } catch (err) {
      error.value = err.message || '프로필을 불러오지 못했습니다';
    } finally {
      loading.value = false;
    }
  };

  const saveProfile = async () => {
    loading.value = true;
    error.value = null;
    try {
      const payload = {
        age: profile.value.age,
        region: profile.value.region,
        interest: profile.value.interests.join(','),
      };
      await saveProfileApi(payload);
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
