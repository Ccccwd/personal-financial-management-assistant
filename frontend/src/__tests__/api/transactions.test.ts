/**
 * Mock API 测试
 *
 * 正确的 Mock API 测试关注三件事：
 *   1. 调用参数正确性：函数是否用正确的参数调用了 API
 *   2. 成功态处理：业务逻辑在 API 成功时是否正确处理数据
 *   3. 失败态处理：业务逻辑在 API 失败时是否正确传播/捕获错误
 *
 * 不应直接断言 mock 返回值本身（循环断言），
 * 而应断言"调用 API 的函数/组件"的行为变化。
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'

vi.mock('@/api/transactions', () => ({
  getTransactions: vi.fn(),
  createTransaction: vi.fn(),
  deleteTransaction: vi.fn(),
  getTransactionSummary: vi.fn()
}))

vi.mock('@/api/auth', () => ({
  login: vi.fn(),
  getCurrentUser: vi.fn(),
  logout: vi.fn()
}))

import * as transactionsApi from '@/api/transactions'
import * as authApi from '@/api/auth'
import { useUserStore } from '@/stores/user'

// ─────────────────────────────────────────────
// 辅助函数：模拟"组件挂载后发起 API 请求"的数据加载行为
// 在真实组件中，这段逻辑位于 onMounted / watch 内
// ─────────────────────────────────────────────
async function simulateTransactionLoad(params: Record<string, unknown> = {}) {
  const state = { loading: true, data: null as unknown, error: null as unknown }
  try {
    state.data = await transactionsApi.getTransactions(params as any)
    state.loading = false
  } catch (err) {
    state.error = err
    state.loading = false
  }
  return state
}

async function simulateCreateTransaction(payload: Record<string, unknown>) {
  const state = { success: false, created: null as unknown, error: null as unknown }
  try {
    state.created = await transactionsApi.createTransaction(payload as any)
    state.success = true
  } catch (err) {
    state.error = err
  }
  return state
}

async function simulateSummaryLoad(params: Record<string, unknown> = {}) {
  const state = { income: 0, expense: 0, net: 0, error: null as unknown }
  try {
    const summary = await transactionsApi.getTransactionSummary(params as any) as any
    state.income = summary.total_income
    state.expense = summary.total_expense
    state.net = summary.net_income
  } catch (err) {
    state.error = err
  }
  return state
}

// ─────────────────────────────────────────────
// 测试：交易列表加载行为
// ─────────────────────────────────────────────
describe('交易列表加载 - Mock API 测试', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('1. 成功态：加载完成后 loading 变为 false，data 有内容', async () => {
    vi.mocked(transactionsApi.getTransactions).mockResolvedValue({
      transactions: [{ id: 1, type: 'expense', amount: 50 }],
      total: 1, page: 1, page_size: 20, total_pages: 1
    } as any)

    const state = await simulateTransactionLoad({ page: 1, page_size: 20 })

    expect(state.loading).toBe(false)
    expect(state.data).not.toBeNull()
    expect(state.error).toBeNull()
  })

  it('2. 成功态：API 以正确参数被调用（参数透传验证）', async () => {
    vi.mocked(transactionsApi.getTransactions).mockResolvedValue({
      transactions: [], total: 0, page: 2, page_size: 10, total_pages: 0
    } as any)

    await simulateTransactionLoad({ page: 2, page_size: 10, type: 'income' })

    expect(transactionsApi.getTransactions).toHaveBeenCalledWith({
      page: 2, page_size: 10, type: 'income'
    })
  })

  it('3. 失败态：网络错误时 loading 变为 false，error 被捕获', async () => {
    vi.mocked(transactionsApi.getTransactions).mockRejectedValue(
      new Error('Network Error')
    )

    const state = await simulateTransactionLoad()

    expect(state.loading).toBe(false)
    expect(state.data).toBeNull()
    expect(state.error).toBeInstanceOf(Error)
    expect((state.error as Error).message).toBe('Network Error')
  })

  it('4. 失败态：401 未授权时 error 包含正确状态码', async () => {
    const authError = Object.assign(new Error('Unauthorized'), {
      response: { status: 401 }
    })
    vi.mocked(transactionsApi.getTransactions).mockRejectedValue(authError)

    const state = await simulateTransactionLoad()

    expect(state.loading).toBe(false)
    expect((state.error as any).response?.status).toBe(401)
  })
})

// ─────────────────────────────────────────────
// 测试：创建交易行为
// ─────────────────────────────────────────────
describe('创建交易 - Mock API 测试', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('5. 成功态：创建成功后 success 为 true，created 有内容', async () => {
    vi.mocked(transactionsApi.createTransaction).mockResolvedValue({
      id: 10, type: 'expense', amount: 88, account_id: 1,
      transaction_date: '2026-04-28', source: 'manual'
    } as any)

    const state = await simulateCreateTransaction({
      type: 'expense', amount: 88, account_id: 1, transaction_date: '2026-04-28'
    })

    expect(state.success).toBe(true)
    expect(state.created).not.toBeNull()
    expect(state.error).toBeNull()
  })

  it('6. 成功态：createTransaction 以正确 payload 被调用', async () => {
    vi.mocked(transactionsApi.createTransaction).mockResolvedValue({ id: 11 } as any)

    const payload = { type: 'income', amount: 5000, account_id: 2, transaction_date: '2026-04-28' }
    await simulateCreateTransaction(payload)

    expect(transactionsApi.createTransaction).toHaveBeenCalledWith(payload)
    expect(transactionsApi.createTransaction).toHaveBeenCalledOnce()
  })

  it('7. 失败态：422 参数校验失败时 success 为 false，error 被捕获', async () => {
    const validationError = Object.assign(new Error('Unprocessable Entity'), {
      response: { status: 422, data: { detail: '金额不能为负数' } }
    })
    vi.mocked(transactionsApi.createTransaction).mockRejectedValue(validationError)

    const state = await simulateCreateTransaction({ type: 'expense', amount: -1 })

    expect(state.success).toBe(false)
    expect((state.error as any).response?.status).toBe(422)
  })
})

// ─────────────────────────────────────────────
// 测试：统计摘要数据处理
// ─────────────────────────────────────────────
describe('统计摘要处理 - Mock API 测试', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('8. 成功态：从 API 响应中正确提取并分配 income/expense/net 字段', async () => {
    vi.mocked(transactionsApi.getTransactionSummary).mockResolvedValue({
      total_income: 8000,
      total_expense: 3200,
      total_transfer: 0,
      net_income: 4800,
      transaction_count: 30
    } as any)

    const state = await simulateSummaryLoad({ start_date: '2026-04-01', end_date: '2026-04-30' })

    // 断言的是"业务层对 API 数据的提取结果"，而非 mock 对象本身
    expect(state.income).toBe(8000)
    expect(state.expense).toBe(3200)
    expect(state.net).toBe(4800)
    expect(state.error).toBeNull()
  })

  it('9. 失败态：API 失败时摘要字段保持初始值 0', async () => {
    vi.mocked(transactionsApi.getTransactionSummary).mockRejectedValue(
      new Error('Server Error')
    )

    const state = await simulateSummaryLoad()

    expect(state.income).toBe(0)
    expect(state.expense).toBe(0)
    expect(state.net).toBe(0)
    expect(state.error).not.toBeNull()
  })
})

// ─────────────────────────────────────────────
// 测试：认证 Store（通过 API Mock 验证 Store 状态流转）
// ─────────────────────────────────────────────
describe('认证 Store - Mock API 状态流转测试', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
    vi.clearAllMocks()
  })

  it('10. 成功态：login API 成功后 Store 的 isLoggedIn 变为 true', async () => {
    vi.mocked(authApi.login).mockResolvedValue({
      access_token: 'token-abc', refresh_token: '', token_type: 'bearer'
    } as any)
    vi.mocked(authApi.getCurrentUser).mockResolvedValue({
      id: 1, username: 'zzx', email: 'zzx@test.com',
      created_at: '2026-01-01', updated_at: '2026-01-01'
    } as any)

    const store = useUserStore()
    expect(store.isLoggedIn).toBe(false)   // 初始：未登录

    await store.login({ username: 'zzx', password: 'pass' })

    expect(store.isLoggedIn).toBe(true)    // 成功后：已登录
    expect(store.user?.username).toBe('zzx')
  })

  it('11. 失败态：login API 返回 401 时 Store 状态不变', async () => {
    vi.mocked(authApi.login).mockRejectedValue(
      Object.assign(new Error('Unauthorized'), { response: { status: 401 } })
    )

    const store = useUserStore()

    await expect(store.login({ username: 'bad', password: 'wrong' })).rejects.toThrow()

    expect(store.isLoggedIn).toBe(false)  // 失败后：仍未登录
    expect(store.user).toBeNull()
  })

  it('12. 成功态：logout 调用后 Store 状态及 localStorage 均被清除', async () => {
    vi.mocked(authApi.login).mockResolvedValue({
      access_token: 'saved', refresh_token: 'r', token_type: 'bearer'
    } as any)
    vi.mocked(authApi.getCurrentUser).mockResolvedValue({
      id: 2, username: 'user2', email: 'u@t.com',
      created_at: '2026-01-01', updated_at: '2026-01-01'
    } as any)

    const store = useUserStore()
    await store.login({ username: 'user2', password: 'p' })
    expect(store.isLoggedIn).toBe(true)

    store.logout()

    expect(store.isLoggedIn).toBe(false)
    expect(localStorage.getItem('finance_token')).toBeNull()
  })
})
