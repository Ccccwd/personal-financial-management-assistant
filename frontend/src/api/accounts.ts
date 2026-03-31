import request from '@/utils/request'
import {
  Account,
  AccountCreate,
  AccountUpdate,
  AccountSummary,
  TransferRequest,
  AdjustBalanceRequest,
  Transaction,
  APIResponse
} from '@/types/index'

/**
 * 获取账户列表
 * @param params 查询参数
 */
export function getAccounts(params?: {
  type?: string
  is_enabled?: boolean
}) {
  return request.get<Account[]>('/accounts', { params })
}

/**
 * 获取账户统计摘要
 */
export function getAccountSummary() {
  return request.get<AccountSummary>('/accounts/summary')
}

/**
 * 获取默认账户
 */
export function getDefaultAccount() {
  return request.get<Account>('/accounts/default')
}

/**
 * 获取账户详情（含统计）
 * @param id 账户ID
 */
export function getAccount(id: number) {
  return request.get<Account>(`/accounts/${id}`)
}

/**
 * 创建账户
 * @param data 账户数据
 */
export function createAccount(data: AccountCreate) {
  return request.post<Account>('/accounts', data)
}

/**
 * 更新账户
 * @param id 账户ID
 * @param data 账户数据
 */
export function updateAccount(id: number, data: AccountUpdate) {
  return request.put<Account>(`/accounts/${id}`, data)
}

/**
 * 删除账户
 * @param id 账户ID
 */
export function deleteAccount(id: number) {
  return request.delete(`/accounts/${id}`)
}

/**
 * 账户间转账
 * @param data 转账数据
 */
export function transfer(data: TransferRequest) {
  return request.post<{
    from_transaction: Transaction
    to_transaction: Transaction
    from_account_balance: number
    to_account_balance: number
  }>('/accounts/transfer', data)
}

/**
 * 调整账户余额
 * @param id 账户ID
 * @param data 调整数据
 */
export function adjustBalance(id: number, data: AdjustBalanceRequest) {
  return request.post<{
    transaction: Transaction
    current_balance: number
  }>(`/accounts/${id}/adjust-balance`, data)
}

/**
 * 获取指定账户的余额历史
 * @param id 账户ID
 * @param params 查询参数
 */
export function getAccountBalanceHistory(id: number, params?: {
  limit?: number
  offset?: number
  change_type?: string
}) {
  return request.get<any[]>(`/accounts/${id}/balance-history`, { params })
}

/**
 * 获取所有账户的余额历史
 * @param params 查询参数
 */
export function getAllBalanceHistory(params?: {
  limit?: number
  offset?: number
  change_type?: string
}) {
  return request.get<any[]>('/balance-history', { params })
}
