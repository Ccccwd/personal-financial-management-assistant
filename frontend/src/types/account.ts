import { BaseEntity } from './common'

export type AccountType = 'cash' | 'bank' | 'wechat' | 'alipay' | 'meal_card' | 'other'

export interface Account extends BaseEntity {
  name: string
  type: AccountType
  balance: number
  initial_balance: number
  icon?: string
  color?: string
  is_default: boolean
  is_enabled: boolean
  description?: string
  expense_total?: number
  income_total?: number
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
  transaction_date?: string
  remark?: string
}

export interface AdjustBalanceRequest {
  new_balance: number
  remark?: string
}

export interface AccountSummary {
  total_balance: number
  total_accounts: number
  account_distribution: Array<{
    type: string
    balance: number
    count: number
  }>
}

export interface AccountListPayload {
  accounts: Account[]
  total: number
}

export interface AccountDetail extends Account {
  expense_total?: number
  income_total?: number
}

export interface TransferResponse {
  from_transaction: import('./transaction').Transaction
  to_transaction: import('./transaction').Transaction
  from_account_balance: number
  to_account_balance: number
}

export interface AdjustBalanceResponse {
  transaction: import('./transaction').Transaction
  current_balance: number
}

export interface BalanceHistoryItem {
  id: number
  account_id: number
  transaction_id?: number
  account_name?: string
  change_type: string
  amount_before: number
  amount_after: number
  change_amount: number
  description?: string
  created_at: string
}
