import request from '@/utils/request'
import type { UserLogin, LoginData, UserCreate, User, APIResponse } from '@/types'

export const login = (data: UserLogin) => {
  return request.post<APIResponse<LoginData>>('/auth/login', data) as unknown as Promise<LoginData>
}

export const register = (data: UserCreate) => {
  return request.post<APIResponse<LoginData>>('/auth/register', data) as unknown as Promise<LoginData>
}

export const getUserInfo = () => {
  return request.get<APIResponse<User>>('/users/me') as unknown as Promise<User>
}
