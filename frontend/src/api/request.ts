import axios, { AxiosInstance, InternalAxiosRequestConfig, AxiosResponse, AxiosError } from 'axios'
import { ElMessage } from 'element-plus'
import { TokenManager } from '@/utils/auth'
import { APIResponse } from '@/types'

const service: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '/api',
  timeout: 10000,
  headers: { 'Content-Type': 'application/json' }
})

// Request interceptor
service.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = TokenManager.getAccessToken()
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error: AxiosError) => {
    console.error('Request error:', error)
    return Promise.reject(error)
  }
)

// Response interceptor
service.interceptors.response.use(
  (response: AxiosResponse): any => {
    const res = response.data as APIResponse
    
    // Check custom code from backend
    if (res.code && res.code !== 200) {
      ElMessage.error(res.message || 'Error')
      return Promise.reject(new Error(res.message || 'Error'))
    }
    
    // Return the data part directly if success
    // This allows calling api like: const data = await api.getData()
    return res.data
  },
  async (error: AxiosError) => {
    console.error('Response error:', error)
    
    if (error.response && error.response.status === 401) {
      // Handle unauthorized error (token expired or invalid)
      TokenManager.removeToken()
      
      // Prevent redirecting if already on login page
      if (window.location.pathname !== '/login') {
        ElMessage.error('登录状态已失效，请重新登录')
        window.location.href = '/login'
      }
    } else {
      ElMessage.error(error.message || 'Request failed')
    }
    
    return Promise.reject(error)
  }
)

export default service
