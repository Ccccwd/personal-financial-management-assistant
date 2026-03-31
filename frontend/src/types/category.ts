import { BaseEntity } from './common'

export type CategoryType = 'income' | 'expense'

export interface Category extends BaseEntity {
  name: string
  type: CategoryType
  icon?: string
  color?: string
  parent_id?: number
  sort_order: number
  is_system: boolean
  children?: Category[]
}

export interface CategoryCreate {
  name: string
  type: CategoryType
  icon?: string
  color?: string
  parent_id?: number
  sort_order?: number
}

export interface CategoryUpdate extends Partial<CategoryCreate> {}

export interface CategoryStat extends Category {
  amount: number
  percent: number
  transaction_count: number
}
