import { defineStore } from 'pinia'
import { ref } from 'vue'
import { apiClient } from '../api'

export interface LogMessage {
  id: number;
  text: string;
  type: 'info' | 'warning' | 'success' | 'error';
}

export const useGenerationStore = defineStore('generation', () => {
  const isGenerating = ref(false)
  const currentResource = ref<any>(null)
  
  const activeNode = ref<string | null>(null)
  const streamLogs = ref<LogMessage[]>([])

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

  const generateResourceStream = async (profileData: any) => {
    isGenerating.value = true
    activeNode.value = null
    streamLogs.value = []
    
    let logId = 0
    const addLog = (text: string, type: LogMessage['type'] = 'info') => {
      streamLogs.value.push({ id: logId++, text, type })
    }
    
    addLog('🚀 [System] 正在初始化多智能体协同管线...', 'info')

    try {
      // 假设后端运行在 8001
      const response = await fetch('http://127.0.0.1:8001/generation/stream', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(profileData)
      })

      if (!response.body) throw new Error('ReadableStream not supported.')

      const reader = response.body.getReader()
      const decoder = new TextDecoder('utf-8')
      let done = false
      let buffer = ''

      while (!done) {
        const { value, done: readerDone } = await reader.read()
        done = readerDone
        if (value) {
          buffer += decoder.decode(value, { stream: true })
          const lines = buffer.split('\n\n')
          
          // 保留最后一块不完整的 chunk 到下一次解析
          buffer = lines.pop() || ''
          
          for (const line of lines) {
            if (line.startsWith('data: ')) {
              const dataStr = line.substring(6)
              try {
                const data = JSON.parse(dataStr)
                if (data.is_complete) {
                  currentResource.value = data
                  addLog('🎉 [System] 所有流程执行完毕！即将进入沉浸学习区...', 'success')
                  activeNode.value = 'complete'
                  break
                }
                
                if (data.node) activeNode.value = data.node
                if (data.message) {
                  addLog(`[${new Date().toLocaleTimeString()}] ${data.message}`, data.status || 'info')
                }
              } catch (e) {
                console.error("Failed to parse chunk:", dataStr)
              }
            }
          }
        }
      }
      return currentResource.value
    } catch (error: any) {
      addLog(`❌ [System] 执行出错: ${error.message}`, 'error')
      throw error
    } finally {
      isGenerating.value = false
    }
  }
  
  return { isGenerating, currentResource, activeNode, streamLogs, generateResource, generateResourceStream }
})
