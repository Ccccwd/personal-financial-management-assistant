import { BaseEntity } from './common'
export type TransactionType = 'income' | 'expense' | 'transfer'
export type TransactionSource = 'manual' | 'wechat' | 'alipay'

export interface Transaction extends BaseEntity {
  type: TransactionType
  amount: number
  category_id?: number | null
  category_name?: string
  category_icon?: string
  account_id: number
  account_name: string
  to_account_id?: number
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
  is_repeated?: boolean
}

export interface TransactionCreate {
  type: TransactionType
  amount: number
  category_id?: number | null
  account_id: number
  to_account_id?: number
  transaction_date: string
  remark?: string
  merchant_name?: string
  product_name?: string
  tags?: string[]
  location?: string
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
  total_transfer: number
  net_income: number
  transaction_count: number
}

export interface TransactionListPayload {
  transactions: Transaction[]
  total: number
  page: number
  page_size: number
  total_pages: number
}
