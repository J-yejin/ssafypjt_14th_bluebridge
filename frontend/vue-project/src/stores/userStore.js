import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { fetchProfile, saveProfile as saveProfileApi } from '../api/client';

// 백엔드 프로필 스키마와 동기화
const emptyProfile = {
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

export const useUserStore = defineStore('user', () => {
  const profile = ref({ ...emptyProfile });
  const loading = ref(false);
  const error = ref(null);

  // 필수 항목 입력 확인
  const isProfileComplete = computed(() => {
    const current = profile.value;
    return Boolean(
      current.age &&
        current.region &&
        current.interests.length > 0 &&
        current.gender &&
        current.employmentStatus &&
        current.educationLevel &&
        current.major &&
        (current.specialTargets || []).length > 0
    );
  });

  const updateProfile = (newProfile) => {
    profile.value = {
      ...profile.value,
      ...newProfile,
      interests: [...(newProfile.interests ?? profile.value.interests ?? [])],
      specialTargets: [...(newProfile.specialTargets ?? profile.value.specialTargets ?? [])],
    };
  };

  const loadProfile = async () => {
    loading.value = true;
    error.value = null;
    try {
      const data = await fetchProfile();
      if (data) {
        const interests = data.interest ? data.interest.split(',').map((v) => v.trim()).filter(Boolean) : [];
        profile.value = {
          ...emptyProfile,
          age: data.age || '',
          region: data.region || '',
          interests,
          gender: data.gender || '',
          householdIncome: data.household_income || '',
          familySize: data.family_size || '',
          incomeQuintile: data.income_quintile || '',
          employmentStatus: data.employment_status || '',
          educationLevel: data.education_level || '',
          major: data.major || '',
          specialTargets: Array.isArray(data.special_targets) ? data.special_targets : [],
        };
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
      const payload = {
        age: profile.value.age,
        region: profile.value.region,
        interest: profile.value.interests.join(','),
        gender: profile.value.gender || '',
        household_income: profile.value.householdIncome || null,
        family_size: profile.value.familySize || null,
        employment_status: profile.value.employmentStatus || '',
        education_level: profile.value.educationLevel || '',
        major: profile.value.major || '',
        special_targets: profile.value.specialTargets || [],
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
