export interface AIClassifyItem {
  merchant_name: string
  product_name?: string
  wechat_category?: string
  amount?: number
  transaction_type?: 'income' | 'expense'
}

export interface AIClassifyResult {
  index: number
  merchant_name: string
  category_id: number | null
  category_name: string
  confidence: number
  matched_by: 'rule' | 'llm'
}

export interface AIClassifyResponse {
  results: AIClassifyResult[]
  total: number
  llm_called_count: number
  rule_matched_count: number
}

export interface ReclassifyResponse {
  transaction_id: number
  category_id: number | null
  category_name: string
  confidence: number
  matched_by: 'rule' | 'llm'
}

export interface AIAdviceAnalysisPeriod {
  start: string
  end: string
}

export interface AIAdviceBudgetBreakdownItem {
  category: string
  suggested_amount: number
}

export interface AIAdviceContent {
  highlights: string[]
  warnings: string[]
  suggestions: string[]
  next_month_budget: {
    total: number
    breakdown: AIAdviceBudgetBreakdownItem[]
  }
  full_report: string
}

export interface AIAdviceResponse {
  generated_at: string
  from_cache: boolean
  analysis_period: AIAdviceAnalysisPeriod
  advice: AIAdviceContent
}

export interface AIAdviceHistoryItem {
  id: number
  advice_type?: string
  generated_at?: string
  created_at: string
  analysis_period: AIAdviceAnalysisPeriod
  highlights?: string[]
  warnings?: string[]
  suggestions?: string[]
  tokens_used?: number
  summary?: string
}

export interface AIAdviceHistoryPayload {
  items: AIAdviceHistoryItem[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

export interface AIAdviceDetail {
  id: number
  advice_type?: string
  created_at: string
  analysis_period: AIAdviceAnalysisPeriod
  highlights?: string[]
  warnings?: string[]
  suggestions?: string[]
  next_month_budget?: {
    total: number
    breakdown: AIAdviceBudgetBreakdownItem[]
  }
  full_report?: string
  tokens_used?: number
}

export interface AIUsage {
  month: string
  classify_calls: number
  advice_calls: number
  total_tokens_used: number
  estimated_cost_cny?: number
}
