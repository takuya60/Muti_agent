import { defineStore } from 'pinia'
import { ref } from 'vue'
import { apiClient } from '../api'

export const useGenerationStore = defineStore('generation', () => {
  const isGenerating = ref(false)
  const currentResource = ref<any>(null)
  
  const generateResource = async (profileData: any) => {
    isGenerating.value = true
    try {
      const res = await apiClient.post('/generation/run', profileData)
      currentResource.value = res.data
      return res.data
    } finally {
      isGenerating.value = false
    }
  }
  
  return { isGenerating, currentResource, generateResource }
})
