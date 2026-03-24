export interface User {
  id: number
  username: string
  email: string
  phone?: string
  avatar?: string
  is_active: boolean
  role?: string
  created_at: string
  updated_at?: string
}

export interface UserResponse {
  data: User
}

export interface UserCreate {
  username: string
  email: string
  password: string
  phone?: string
}

export interface UserLogin {
  username: string
  password: string
}

export interface Token {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface LoginData {
  token: Token
  user: User
}
