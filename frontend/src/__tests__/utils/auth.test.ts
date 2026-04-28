/**
 * TokenManager 工具类测试
 * 测试 Token 的存取、删除等核心功能
 */
import { describe, it, expect, beforeEach } from 'vitest'
import { TokenManager } from '@/utils/auth'

describe('TokenManager 工具类', () => {
  beforeEach(() => {
    localStorage.clear()
  })

  it('1. setToken 能正确保存 access_token', () => {
    TokenManager.setToken({
      access_token: 'test-access-token',
      refresh_token: 'test-refresh-token',
      token_type: 'bearer'
    })
    expect(localStorage.getItem('finance_token')).toBe('test-access-token')
  })

  it('2. setToken 能正确保存 refresh_token', () => {
    TokenManager.setToken({
      access_token: 'test-access-token',
      refresh_token: 'test-refresh-token',
      token_type: 'bearer'
    })
    expect(localStorage.getItem('finance_refresh_token')).toBe('test-refresh-token')
  })

  it('3. getAccessToken 能正确读取 access_token', () => {
    localStorage.setItem('finance_token', 'my-token')
    expect(TokenManager.getAccessToken()).toBe('my-token')
  })

  it('4. getRefreshToken 能正确读取 refresh_token', () => {
    localStorage.setItem('finance_refresh_token', 'my-refresh')
    expect(TokenManager.getRefreshToken()).toBe('my-refresh')
  })

  it('5. removeToken 能删除所有 Token', () => {
    localStorage.setItem('finance_token', 'token-1')
    localStorage.setItem('finance_refresh_token', 'refresh-1')
    TokenManager.removeToken()
    expect(TokenManager.getAccessToken()).toBeNull()
    expect(TokenManager.getRefreshToken()).toBeNull()
  })

  it('6. 未设置时 getAccessToken 返回 null', () => {
    expect(TokenManager.getAccessToken()).toBeNull()
  })

  it('7. 未设置时 getRefreshToken 返回 null', () => {
    expect(TokenManager.getRefreshToken()).toBeNull()
  })

  it('8. 空字符串 refresh_token 不会被存入', () => {
    TokenManager.setToken({
      access_token: 'token',
      refresh_token: '',
      token_type: 'bearer'
    })
    expect(localStorage.getItem('finance_refresh_token')).toBeNull()
  })
})
