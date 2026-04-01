import request from '@/utils/request'
import {
  Transaction,
  TransactionCreate,
  TransactionListPayload,
  TransactionUpdate,
  TransactionQuery,
  TransactionSummary
} from '@/types/index'

/**
 * 获取交易列表
 * @param params 查询参数
 */
export function getTransactions(params?: TransactionQuery) {
  return request.get<TransactionListPayload>('/transactions', { params })
}

/**
 * 获取交易统计摘要
 * @param params 查询参数
 */
export function getTransactionSummary(params?: {
  start_date?: string
  end_date?: string
  type?: string
}) {
  return request.get<TransactionSummary>('/transactions/summary', { params })
}

/**
 * 获取交易统计摘要（文档别名）
 * @param params 查询参数
 */
export function getTransactionStatistics(params?: {
  start_date?: string
  end_date?: string
  type?: string
}) {
  return request.get<TransactionSummary>('/transactions/statistics', { params })
}

/**
 * 搜索交易记录
 * @param params 查询参数
 */
export function searchTransactions(params: {
  keyword: string
  limit?: number
}) {
  return request.get<Transaction[]>('/transactions/search', { params })
}

/**
 * 获取交易详情
 * @param id 交易ID
 */
export function getTransaction(id: number) {
  return request.get<Transaction>(`/transactions/${id}`)
}

/**
 * 创建交易记录
 * @param data 交易数据
 */
export function createTransaction(data: TransactionCreate) {
  return request.post<Transaction>('/transactions', data)
}

/**
 * 更新交易记录
 * @param id 交易ID
 * @param data 交易数据
 */
export function updateTransaction(id: number, data: TransactionUpdate) {
  return request.put<Transaction>(`/transactions/${id}`, data)
}

/**
 * 删除交易记录
 * @param id 交易ID
 */
export function deleteTransaction(id: number) {
  return request.delete(`/transactions/${id}`)
}

/**
 * 标记交易为重复
 * @param id 交易ID
 */
export function markTransactionRepeated(id: number) {
  return request.post<{ message?: string }>(`/transactions/${id}/mark-repeated`)
}
