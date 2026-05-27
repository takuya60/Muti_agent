import { defineStore } from 'pinia'
import { ref } from 'vue'
import { apiClient } from '../api'

export const useLearnerStore = defineStore('learner', () => {
  const currentLearner = ref<any>(null)
  
  const getExampleProfiles = async () => {
    const res = await apiClient.get('/learners/examples')
    return res.data
  }
  
  const login = async (profileData: any) => {
    const res = await apiClient.post('/learners/validate', profileData)
    currentLearner.value = res.data.profile
    return res.data
  }
  
  return { currentLearner, getExampleProfiles, login }
})
