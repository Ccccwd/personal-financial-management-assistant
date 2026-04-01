import request from '@/utils/request'
import {
  Token,
  LoginData,
  User,
  UserCreate,
  UserLogin,
  UserResponse,
  UpdateCurrentUserRequest,
  ChangePasswordRequest,
  PasswordResetTokenRequest,
  PasswordResetEmailRequest,
  VerifyEmailForResetResponse
} from '@/types/index'

/**
 * 用户注册
 * @param data 注册数据
 */
export function register(data: UserCreate) {
  return request.post<UserResponse>('/auth/register', data)
}

/**
 * 用户登录
 * @param data 登录数据
 */
export function login(data: UserLogin) {
  return request.post<LoginData>('/auth/login', data)
}

/**
 * 刷新 Token
 * @param refreshToken 刷新令牌
 */
export function refreshToken(refreshToken: string) {
  return request.post<Token>('/auth/refresh', null, {
    params: {
      refresh_token: refreshToken
    }
  })
}

/**
 * 用户登出
 */
export function logout() {
  return request.post<{ message: string }>('/auth/logout')
}

/**
 * 获取当前用户信息
 */
export function getCurrentUser() {
  return request.get<User>('/auth/me')
}

/**
 * 更新当前用户信息
 * @param data 更新数据
 */
export function updateCurrentUser(data: Partial<User>) {
  return request.put<User>('/auth/me', data)
}

/**
 * 更新当前用户信息
 * @param data 更新数据
 */
export function updateCurrentUserProfile(data: UpdateCurrentUserRequest) {
  return request.put<User>('/auth/me', data)
}

/**
 * 修改密码
 * @param data 密码数据
 */
export function changePassword(data: {
  old_password: string
  new_password: string
}) {
  return request.post<{ message: string }>('/auth/change-password', data)
}

/**
 * 修改密码
 * @param data 密码数据
 */
export function changePasswordRequest(data: ChangePasswordRequest) {
  return request.post<{ message: string }>('/auth/change-password', data)
}

/**
 * 请求密码重置
 * @param email 邮箱
 */
export function requestPasswordReset(email: string) {
  return request.post<{ message: string }>('/auth/password-reset-request', { email })
}

/**
 * 通过 Token 重置密码
 * @param data 重置数据
 */
export function resetPasswordWithToken(data: {
  token: string
  new_password: string
}) {
  return request.post<{ message: string }>('/auth/password-reset', data)
}

/**
 * 通过 Token 重置密码
 * @param data 重置数据
 */
export function resetPasswordByToken(data: PasswordResetTokenRequest) {
  return request.post<{ message: string }>('/auth/password-reset', data)
}

/**
 * 直接通过邮箱重置密码
 * @param data 重置数据
 */
export function resetPasswordDirectly(data: {
  email: string
  new_password: string
}) {
  return request.post<{ message: string }>('/auth/reset-password', data)
}

/**
 * 直接通过邮箱重置密码
 * @param data 重置数据
 */
export function resetPasswordByEmail(data: PasswordResetEmailRequest) {
  return request.post<{ message: string }>('/auth/reset-password', data)
}

/**
 * 验证邮箱是否存在
 * @param email 邮箱
 */
export function verifyEmailForReset(email: string) {
  return request.post<VerifyEmailForResetResponse>('/auth/verify-email-for-reset', { email })
}
