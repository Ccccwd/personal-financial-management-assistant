import request from '@/api/request'
import {
  Category,
  CategoryCreate,
  CategoryListPayload,
  CategoryUpdate,
  CategoryStat,
} from '@/types/index'

/** 按 (type, name) 去重，保留首次出现的条目 */
function deduplicateCategories(categories: Category[]): Category[] {
  const seen = new Set<string>()
  return categories.filter(c => {
    const key = `${c.type}:${c.name}`
    if (seen.has(key)) return false
    seen.add(key)
    return true
  })
}

/**
 * 初始化当前用户的系统预设分类
 */
export function initSystemCategories() {
  return request.post<{ created_count: number }>('/categories/init-system')
}

/**
 * 获取分类列表
 * @param params 查询参数
 */
export async function getCategories(params?: {
  type?: 'expense' | 'income'
  include_system?: boolean
  parent_id?: number
}): Promise<CategoryListPayload> {
  const res = await request.get<CategoryListPayload>('/categories', { params }) as unknown as CategoryListPayload
  if (res?.categories) {
    res.categories = deduplicateCategories(res.categories)
    res.total = res.categories.length
  }
  return res
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
