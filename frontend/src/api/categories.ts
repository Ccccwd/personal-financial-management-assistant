import request from '@/utils/request'
import {
  Category,
  CategoryCreate,
  CategoryUpdate,
  CategoryStat,
  APIResponse
} from '@/types/index'

/**
 * 获取分类列表
 * @param params 查询参数
 */
export function getCategories(params?: {
  type?: 'expense' | 'income'
  include_system?: boolean
  parent_id?: number
}) {
  return request.get<Category[]>('/categories', { params })
}

/**
 * 获取分类树
 * @param params 查询参数
 */
export function getCategoryTree(params?: {
  type?: 'expense' | 'income'
  include_system?: boolean
}) {
  return request.get<Category[]>('/categories/tree', { params })
}

/**
 * 获取带使用统计的分类列表
 * @param params 查询参数
 */
export function getCategoryStats(params?: {
  type?: 'expense' | 'income'
  limit?: number
}) {
  return request.get<CategoryStat[]>('/categories/stats', { params })
}

/**
 * 获取分类详情
 * @param id 分类ID
 */
export function getCategory(id: number) {
  return request.get<Category>(`/categories/${id}`)
}

/**
 * 创建分类
 * @param data 分类数据
 */
export function createCategory(data: CategoryCreate) {
  return request.post<Category>('/categories', data)
}

/**
 * 更新分类
 * @param id 分类ID
 * @param data 分类数据
 */
export function updateCategory(id: number, data: CategoryUpdate) {
  return request.put<Category>(`/categories/${id}`, data)
}

/**
 * 删除分类
 * @param id 分类ID
 */
export function deleteCategory(id: number) {
  return request.delete(`/categories/${id}`)
}
