import { getCategories, initSystemCategories } from '@/api/categories'
import type { Category, CategoryListPayload, CategoryType } from '@/types/category'

/**
 * 加载当前用户分类；若为空则自动初始化系统预设分类后重试。
 */
export async function ensureCategoriesLoaded(type?: CategoryType): Promise<Category[]> {
  const params = type ? { type } : undefined
  let payload = await getCategories(params) as unknown as CategoryListPayload
  let list = payload?.categories ?? []

  if (list.length === 0) {
    await initSystemCategories()
    payload = await getCategories(params) as unknown as CategoryListPayload
    list = payload?.categories ?? []
  }

  return list
}
