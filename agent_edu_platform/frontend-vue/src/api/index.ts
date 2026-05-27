import axios from 'axios'
import { ElMessage } from 'element-plus'

export const apiClient = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 30000 // 30 seconds for LLM generation
})

// 响应拦截器统一处理错误
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    const msg = error.response?.data?.detail || error.message || '未知错误'
    // 结合技术纪实与情感化设计的错误提示 (用户需求)
    ElMessage.error(`糟糕，老师的思路卡壳了，请尝试刷新重试 😢 | 大模型请求超时或出错：${msg}`)
    return Promise.reject(error)
  }
)
