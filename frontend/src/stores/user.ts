import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { login as loginApi, getCurrentUser as getUserInfoApi } from '@/api/auth'
import { TokenManager } from '@/utils/auth'
import type { User, UserLogin } from '@/types'

export const useUserStore = defineStore('user', () => {
  const user = ref<User | null>(null)
  const token = ref<string | null>(TokenManager.getAccessToken())

  const isLoggedIn = computed(() => !!token.value)

  /**
   * 用户登录
   */
  const login = async (loginData: UserLogin) => {
    try {
      const response = await loginApi(loginData) as unknown as {
        access_token: string
        refresh_token?: string
        token_type: string
      }
      const { access_token, refresh_token } = response
      
      if (access_token) {
        token.value = access_token
        TokenManager.setToken({ 
          access_token, 
          refresh_token: refresh_token || '', 
          token_type: 'bearer' 
        })
        
        // 登录成功后获取用户信息
        await getUserInfo()
        return true
      }
      return false
    } catch (error) {
      console.error('Login failed:', error)
      throw error
    }
  }

  /**
   * 获取当前用户信息
   */
  const getUserInfo = async () => {
    try {
      const response = await getUserInfoApi() as unknown as User
      user.value = response
      return response
    } catch (error) {
      console.error('Get user info failed:', error)
      // 如果获取用户信息失败（可能是 token 过期），则清空登录状态
      logout()
      throw error
    }
  }

  /**
   * 用户退出
   */
  const logout = () => {
    token.value = null
    user.value = null
    TokenManager.removeToken()
  }

  return {
    user,
    token,
    isLoggedIn,
    login,
    getUserInfo,
    logout
  }
})
