/**
 * User Store 测试
 * 测试用户状态管理：登录、登出、用户信息获取
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useUserStore } from '@/stores/user'

// Mock API 模块
vi.mock('@/api/auth', () => ({
  login: vi.fn(),
  getCurrentUser: vi.fn(),
  logout: vi.fn()
}))

import * as authApi from '@/api/auth'

describe('User Store', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    vi.clearAllMocks()
    vi.spyOn(console, 'error').mockImplementation(() => {})
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('1. 初始状态：未登录，用户为 null', () => {
    const store = useUserStore()
    expect(store.isLoggedIn).toBe(false)
    expect(store.user).toBeNull()
  })

  it('2. 登录成功后 isLoggedIn 变为 true', async () => {
    vi.mocked(authApi.login).mockResolvedValue({
      access_token: 'mock-access-token',
      refresh_token: 'mock-refresh-token',
      token_type: 'bearer'
    } as any)

    vi.mocked(authApi.getCurrentUser).mockResolvedValue({
      id: 1,
      username: 'testuser',
      email: 'test@example.com',
      created_at: '2026-01-01',
      updated_at: '2026-01-01'
    } as any)

    const store = useUserStore()
    const result = await store.login({ username: 'testuser', password: 'Test@1234' })

    expect(result).toBe(true)
    expect(store.isLoggedIn).toBe(true)
  })

  it('3. 登录成功后用户信息被正确存储', async () => {
    vi.mocked(authApi.login).mockResolvedValue({
      access_token: 'mock-token',
      refresh_token: '',
      token_type: 'bearer'
    } as any)

    vi.mocked(authApi.getCurrentUser).mockResolvedValue({
      id: 1,
      username: 'alice',
      email: 'alice@example.com',
      created_at: '2026-01-01',
      updated_at: '2026-01-01'
    } as any)

    const store = useUserStore()
    await store.login({ username: 'alice', password: 'pass' })

    expect(store.user?.username).toBe('alice')
    expect(store.user?.email).toBe('alice@example.com')
  })

  it('4. 登录失败时抛出异常', async () => {
    vi.mocked(authApi.login).mockRejectedValue(new Error('401 Unauthorized'))

    const store = useUserStore()

    await expect(
      store.login({ username: 'bad', password: 'wrong' })
    ).rejects.toThrow('401 Unauthorized')
  })

  it('5. 退出登录后 isLoggedIn 变为 false，用户信息清除', async () => {
    vi.mocked(authApi.login).mockResolvedValue({
      access_token: 'mock-token',
      refresh_token: 'mock-refresh',
      token_type: 'bearer'
    } as any)

    vi.mocked(authApi.getCurrentUser).mockResolvedValue({
      id: 1,
      username: 'user',
      email: 'u@e.com',
      created_at: '2026-01-01',
      updated_at: '2026-01-01'
    } as any)

    const store = useUserStore()
    await store.login({ username: 'user', password: 'pass' })
    expect(store.isLoggedIn).toBe(true)

    store.logout()

    expect(store.isLoggedIn).toBe(false)
    expect(store.user).toBeNull()
    expect(store.token).toBeNull()
  })

  it('6. 登录成功后 Token 被正确写入 localStorage', async () => {
    vi.mocked(authApi.login).mockResolvedValue({
      access_token: 'saved-token',
      refresh_token: 'saved-refresh',
      token_type: 'bearer'
    } as any)

    vi.mocked(authApi.getCurrentUser).mockResolvedValue({
      id: 1,
      username: 'user',
      email: 'u@e.com',
      created_at: '2026-01-01',
      updated_at: '2026-01-01'
    } as any)

    const store = useUserStore()
    await store.login({ username: 'user', password: 'pass' })

    expect(localStorage.getItem('finance_token')).toBe('saved-token')
  })

  it('7. 退出登录后 localStorage 中的 Token 被清除', async () => {
    localStorage.setItem('finance_token', 'some-token')
    localStorage.setItem('finance_refresh_token', 'some-refresh')

    const store = useUserStore()
    store.logout()

    expect(localStorage.getItem('finance_token')).toBeNull()
  })
})
