import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { Category, CategoryType } from '@/types/category'
import { getCategories, createCategory, updateCategory, deleteCategory } from '@/api/categories'
import type { CategoryListPayload } from '@/types/category'

const STORAGE_KEY = 'local_categories'

let _nextId = -1
const localId = () => _nextId--

/** 内置默认分类（is_system = true，id 为负数，仅作前端标识） */
const DEFAULT_CATEGORIES: Category[] = [
  { id: -1,  name: '餐饮美食', type: 'expense', icon: '🍔', color: '#F59E0B', sort_order: 1,  is_system: true, created_at: '', updated_at: '' },
  { id: -2,  name: '交通出行', type: 'expense', icon: '🚗', color: '#3B82F6', sort_order: 2,  is_system: true, created_at: '', updated_at: '' },
  { id: -3,  name: '日常购物', type: 'expense', icon: '🛒', color: '#8B5CF6', sort_order: 3,  is_system: true, created_at: '', updated_at: '' },
  { id: -4,  name: '娱乐休闲', type: 'expense', icon: '🎮', color: '#EC4899', sort_order: 4,  is_system: true, created_at: '', updated_at: '' },
  { id: -5,  name: '居家生活', type: 'expense', icon: '🏠', color: '#10B981', sort_order: 5,  is_system: true, created_at: '', updated_at: '' },
  { id: -6,  name: '医疗健康', type: 'expense', icon: '💊', color: '#EF4444', sort_order: 6,  is_system: true, created_at: '', updated_at: '' },
  { id: -7,  name: '教育培训', type: 'expense', icon: '📚', color: '#06B6D4', sort_order: 7,  is_system: true, created_at: '', updated_at: '' },
  { id: -8,  name: '服饰装扮', type: 'expense', icon: '👗', color: '#F97316', sort_order: 8,  is_system: true, created_at: '', updated_at: '' },
  { id: -9,  name: '人情往来', type: 'expense', icon: '🎁', color: '#84CC16', sort_order: 9,  is_system: true, created_at: '', updated_at: '' },
  { id: -10, name: '旅行出游', type: 'expense', icon: '✈️', color: '#14B8A6', sort_order: 10, is_system: true, created_at: '', updated_at: '' },
  { id: -11, name: '工资薪资', type: 'income',  icon: '💰', color: '#16A34A', sort_order: 1,  is_system: true, created_at: '', updated_at: '' },
  { id: -12, name: '奖金',     type: 'income',  icon: '🎯', color: '#059669', sort_order: 2,  is_system: true, created_at: '', updated_at: '' },
  { id: -13, name: '理财投资', type: 'income',  icon: '📈', color: '#0EA5E9', sort_order: 3,  is_system: true, created_at: '', updated_at: '' },
  { id: -14, name: '兼职收入', type: 'income',  icon: '💼', color: '#7C3AED', sort_order: 4,  is_system: true, created_at: '', updated_at: '' },
  { id: -15, name: '其他收入', type: 'income',  icon: '🌟', color: '#D97706', sort_order: 5,  is_system: true, created_at: '', updated_at: '' },
]

function loadFromStorage(): Category[] | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? (JSON.parse(raw) as Category[]) : null
  } catch {
    return null
  }
}

function saveToStorage(list: Category[]) {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(list))
  } catch {
    // 存储失败时静默处理
  }
}

export const useCategoryStore = defineStore('category', () => {
  /** 全量分类列表（包含默认 + 用户自定义） */
  const categories = ref<Category[]>(loadFromStorage() ?? [...DEFAULT_CATEGORIES])
  const synced = ref(false)

  /** 从后端同步（仅在后端可用时生效，失败静默） */
  async function syncFromBackend() {
    if (synced.value) return
    try {
      const res = await getCategories() as unknown as CategoryListPayload
      if (res?.categories?.length) {
        categories.value = res.categories
        synced.value = true
        saveToStorage(categories.value)
      }
    } catch {
      // 后端未就绪，继续使用本地分类
    }
  }

  /** 按类型过滤 */
  function getByType(type: CategoryType) {
    return categories.value.filter(c => c.type === type)
  }

  /** 新增本地分类 */
  async function addCategory(data: { name: string; type: CategoryType; icon?: string; color?: string }) {
    if (synced.value) {
      const res = await createCategory(data) as unknown as Category
      categories.value.push(res)
      saveToStorage(categories.value)
      return res
    }
    const newCat: Category = {
      id: localId(),
      name: data.name,
      type: data.type,
      icon: data.icon,
      color: data.color,
      sort_order: categories.value.filter(c => c.type === data.type).length + 1,
      is_system: false,
      created_at: new Date().toISOString(),
      updated_at: new Date().toISOString(),
    }
    categories.value.push(newCat)
    saveToStorage(categories.value)
    return newCat
  }

  /** 更新本地分类 */
  async function editCategory(id: number, data: { name?: string; icon?: string; color?: string }) {
    if (synced.value && id > 0) {
      const res = await updateCategory(id, data) as unknown as Category
      const idx = categories.value.findIndex(c => c.id === id)
      if (idx !== -1) categories.value[idx] = res
      saveToStorage(categories.value)
      return
    }
    const target = categories.value.find(c => c.id === id)
    if (target) {
      Object.assign(target, data, { updated_at: new Date().toISOString() })
      saveToStorage(categories.value)
    }
  }

  /** 删除本地分类（系统分类不允许删除） */
  async function removeCategory(id: number) {
    const target = categories.value.find(c => c.id === id)
    if (!target || target.is_system) return
    if (synced.value && id > 0) {
      await deleteCategory(id)
    }
    categories.value = categories.value.filter(c => c.id !== id)
    saveToStorage(categories.value)
  }

  /** 重置为默认分类 */
  function resetToDefaults() {
    categories.value = [...DEFAULT_CATEGORIES]
    synced.value = false
    saveToStorage(categories.value)
  }

  return { categories, synced, syncFromBackend, getByType, addCategory, editCategory, removeCategory, resetToDefaults }
})
