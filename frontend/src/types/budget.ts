import { BaseEntity } from './common'

export type BudgetPeriodType = 'monthly' | 'yearly'
export type BudgetStatus = 'normal' | 'warning' | 'exceeded'

export interface BudgetCategoryInfo {
  id: number
  name: string
  icon?: string
  color?: string
}

export interface Budget extends BaseEntity {
  category_id: number | null
  amount: number
  period_type: BudgetPeriodType
  year: number
  month?: number
  alert_threshold: number
  is_enabled: boolean
}

export interface BudgetWithProgress extends Budget {
  category?: BudgetCategoryInfo
  actual_spending: number
  remaining: number
  percentage: number
  status: BudgetStatus
}

export interface BudgetCreate {
  category_id: number | null
  amount: number
  period_type: BudgetPeriodType
  year: number
  month?: number
  alert_threshold?: number
  is_enabled?: boolean
}

export interface BudgetUpdate {
  category_id?: number | null
  amount?: number
  period_type?: BudgetPeriodType
  year?: number
  month?: number
  alert_threshold?: number
  is_enabled?: boolean
}

export interface BudgetQuery {
  year: number
  month?: number
  period_type?: BudgetPeriodType
}

export interface BudgetListPayload {
  year: number
  month?: number
  budgets: BudgetWithProgress[]
}
