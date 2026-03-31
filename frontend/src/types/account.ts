import { BaseEntity } from './common'

export type AccountType = 'cash' | 'bank' | 'wechat' | 'alipay' | 'meal_card' | 'other'

export interface Account extends BaseEntity {
  user_id: number
  name: string
  type: AccountType
  balance: number
  initial_balance: number
  icon?: string
  color?: string
  is_default: boolean
  is_enabled: boolean
  description?: string
  expense_total?: number // For account details with stats
  income_total?: number  // For account details with stats
}

export interface AccountCreate {
  name: string
  type: AccountType
  initial_balance: number
  icon?: string
  color?: string
  is_default?: boolean
  description?: string
}

export interface AccountUpdate extends Partial<AccountCreate> {
  is_enabled?: boolean
}

export interface TransferRequest {
  from_account_id: number
  to_account_id: number
  amount: number
  transaction_date: string
  remark?: string
}

export interface AdjustBalanceRequest {
  new_balance: number
  remark?: string
}

export interface AccountSummary {
  total_assets: number
  total_liability: number // if negative balance is allowed
  net_assets: number
  account_count: number
}
