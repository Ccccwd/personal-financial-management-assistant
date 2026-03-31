import { BaseEntity } from './common'
import { Category } from './category'
import { Account } from './account'

export type TransactionType = 'income' | 'expense' | 'transfer'
export type TransactionSource = 'manual' | 'wechat' | 'alipay'

export interface Transaction extends BaseEntity {
  user_id: number
  type: TransactionType
  amount: number
  category_id: number
  category?: Category
  account_id: number
  account?: Account
  to_account_id?: number
  to_account?: Account
  transaction_date: string
  remark?: string
  merchant_name?: string
  product_name?: string
  source: TransactionSource
  wechat_transaction_id?: string
  tags?: string[]
  location?: string
  images?: string[]
  ai_classified?: boolean
}

export interface TransactionCreate {
  type: TransactionType
  amount: number
  category_id: number
  account_id: number
  to_account_id?: number
  transaction_date: string
  remark?: string
  merchant_name?: string
  tags?: string[]
  images?: string[]
}

export interface TransactionUpdate extends Partial<TransactionCreate> {}

export interface TransactionQuery {
  page?: number
  page_size?: number
  type?: TransactionType
  category_id?: number
  account_id?: number
  start_date?: string
  end_date?: string
  keyword?: string
  min_amount?: number
  max_amount?: number
  sort_by?: string
  sort_order?: 'asc' | 'desc'
}

export interface TransactionSummary {
  total_income: number
  total_expense: number
  net_income: number
  transaction_count: number
}
