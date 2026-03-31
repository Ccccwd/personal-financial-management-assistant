import { BaseEntity } from './common'

export interface AIClassifyItem {
  merchant_name: string
  product_name?: string
  wechat_category?: string
  amount?: number
  transaction_type?: string
}

export interface AIClassifyResult {
  merchant_name: string
  category_id: number
  category_name: string
  confidence: number
  matched_by: 'rule' | 'llm'
}

export interface AIAdviceRecord extends BaseEntity {
  user_id: number
  generated_at: string
  analysis_start: string
  analysis_end: string
  summary: string
  full_report: string
  highlights: string[] // JSON array in DB
  warnings: string[] // JSON array in DB
  suggestions: string[] // JSON array in DB
  next_month_budget: any // JSON in DB
  tokens_used: number
  from_cache?: boolean // response only
}

export interface AIUsage {
  total_calls: number
  total_tokens: number
  remaining_quota: number // if applicable
}
