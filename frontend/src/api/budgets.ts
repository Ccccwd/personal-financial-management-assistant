import request from '@/api/request'
import {
  Budget,
  BudgetCreate,
  BudgetListPayload,
  BudgetUpdate,
  BudgetQuery
} from '@/types/index'

/**
 * 获取预算列表
 * @param params 查询参数
 */
export function getBudgets(params: BudgetQuery) {
  return request.get<BudgetListPayload>('/budgets', { params })
}

/**
 * 创建预算
 * @param data 预算数据
 */
export function createBudget(data: BudgetCreate) {
  return request.post<Budget>('/budgets', data)
}

/**
 * 更新预算
 * @param id 预算ID
 * @param data 预算数据
 */
export function updateBudget(id: number, data: BudgetUpdate) {
  return request.put<Budget>(`/budgets/${id}`, data)
}

/**
 * 删除预算
 * @param id 预算ID
 */
export function deleteBudget(id: number) {
  return request.delete(`/budgets/${id}`)
}
