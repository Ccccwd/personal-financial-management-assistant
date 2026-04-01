export interface User {
  id: number
  username: string
  email: string
  avatar?: string
  is_active: boolean
  created_at: string
  updated_at?: string
}

export interface UserResponse {
  id: number
  username: string
  email: string
  avatar?: string
  is_active: boolean
  created_at: string
}

export interface UserCreate {
  username: string
  email: string
  password: string
}

export interface UserLogin {
  username: string
  password: string
}

export interface Token {
  access_token: string
  token_type: string
  expires_in?: number
  refresh_token?: string
}

export interface LoginData {
  access_token: string
  token_type: string
  expires_in: number
  refresh_token?: string
}

export interface UpdateCurrentUserRequest {
  username?: string
  avatar?: string
}

export interface ChangePasswordRequest {
  old_password: string
  new_password: string
}

export interface PasswordResetTokenRequest {
  token: string
  new_password: string
}

export interface PasswordResetEmailRequest {
  email: string
  new_password: string
}

export interface VerifyEmailForResetResponse {
  exists: boolean
  message: string
}
