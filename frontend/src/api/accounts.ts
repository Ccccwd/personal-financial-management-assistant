import request from '@/api/request'
import {
  Account,
  AccountCreate,
  AccountDetail,
  AccountListPayload,
  AdjustBalanceResponse,
  AccountUpdate,
  AccountSummary,
  BalanceHistoryItem,
  TransferRequest,
  AdjustBalanceRequest,
  TransferResponse
} from '@/types/index'

/**
 * 获取账户列表
 * @param params 查询参数
 */
export function getAccounts(params?: {
  type?: string
  is_enabled?: boolean
}) {
  return request.get<AccountListPayload>('/accounts', { params })
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
  return request.get<AccountDetail>(`/accounts/${id}`)
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
  return request.post<TransferResponse>('/accounts/transfer', data)
}

/**
 * 调整账户余额
 * @param id 账户ID
 * @param data 调整数据
 */
export function adjustBalance(id: number, data: AdjustBalanceRequest) {
  return request.post<AdjustBalanceResponse>(`/accounts/${id}/adjust-balance`, data)
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
  return request.get<BalanceHistoryItem[]>(`/accounts/${id}/balance-history`, { params })
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
  return request.get<BalanceHistoryItem[]>('/balance-history', { params })
}
