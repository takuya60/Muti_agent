import axios from 'axios'

export const apiClient = axios.create({
  baseURL: 'http://localhost:8001',
  timeout: 120000 // 120 秒：完整多 Agent 流水线（诊断→检索→LLM生成→审核→评估）需要较长时间
})

// 响应拦截器统一处理错误
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const msg = error.response?.data?.detail || error.message || '未知错误'
    console.error(`[AgentEdu] 请求失败：${msg}`)
    return Promise.reject(error)
  }
)
