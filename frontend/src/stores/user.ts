import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { User, UserLogin } from '@/types'
import { login as loginApi, getUserInfo as getUserInfoApi } from '@/api/auth'
import { TokenManager } from '@/utils/auth'

export const useUserStore = defineStore('user', () => {
    const user = ref<User | null>(null)
    const token = ref<string | null>(TokenManager.getAccessToken())

    const login = async (loginData: UserLogin) => {
        try {
            const response = await loginApi(loginData)
            const { access_token, refresh_token } = response.token
            if (access_token) {
                token.value = access_token
                TokenManager.setToken({ access_token, refresh_token, token_type: 'bearer' })
                await getUserInfo()
                return true
            }
            return false
        } catch (error) {
            console.error('Login failed', error)
            throw error
        }
    }

    const getUserInfo = async () => {
        try {
            const response = await getUserInfoApi()
            user.value = response
        } catch (error) {
            console.error('Get user info failed', error)
        }
    }

    const logout = () => {
        token.value = null
        user.value = null
        TokenManager.removeToken()
    }

    return {
        user,
        token,
        login,
        getUserInfo,
        logout
    }
})
