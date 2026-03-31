import { BaseEntity } from './common'

export type BudgetPeriodType = 'monthly' | 'yearly'
export type BudgetStatus = 'normal' | 'warning' | 'exceeded'

export interface Budget extends BaseEntity {
  user_id: number
  category_id: number | null // null for total budget
  category_name?: string // For display
  amount: number
  period_type: BudgetPeriodType
  year: number
  month?: number
  alert_threshold: number
  is_enabled: boolean
  used_amount: number // Calculated field
  usage_percent: number // Calculated field
  remaining_amount: number // Calculated field
  status: BudgetStatus // Calculated field
}

export interface BudgetCreate {
  category_id: number | null
  amount: number
  period_type: BudgetPeriodType
  year: number
  month?: number
  alert_threshold?: number
}

export interface BudgetUpdate {
  amount?: number
  alert_threshold?: number
  is_enabled?: boolean
}

export interface BudgetQuery {
  year: number
  month?: number
  period_type?: BudgetPeriodType
}
