import { Token } from '@/types'

const TOKEN_KEY = 'finance_token'
const REFRESH_TOKEN_KEY = 'finance_refresh_token'
const USER_KEY = 'finance_user'

export class TokenManager {
  static setToken(token: Token): void {
    if (token.access_token) {
      localStorage.setItem(TOKEN_KEY, token.access_token)
    }
    if (token.refresh_token) {
      localStorage.setItem(REFRESH_TOKEN_KEY, token.refresh_token)
    }
  }

  static getAccessToken(): string | null {
    return localStorage.getItem(TOKEN_KEY)
  }

  static getRefreshToken(): string | null {
    return localStorage.getItem(REFRESH_TOKEN_KEY)
  }

  static removeToken(): void {
    localStorage.removeItem(TOKEN_KEY)
    localStorage.removeItem(REFRESH_TOKEN_KEY)
  }
}
