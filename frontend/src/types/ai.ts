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
  category_id: number
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

export interface ReclassifyCategoryInfo {
  id: number
  name: string
}

export interface ReclassifyResponse {
  transaction_id: number
  old_category: ReclassifyCategoryInfo
  new_category: ReclassifyCategoryInfo
  confidence: number
  applied: boolean
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
  generated_at: string
  analysis_period: AIAdviceAnalysisPeriod
  summary: string
}

export interface AIAdviceHistoryPayload {
  records: AIAdviceHistoryItem[]
  total: number
}

export interface AIUsage {
  month: string
  classify_calls: number
  advice_calls: number
  total_tokens_used: number
  estimated_cost_cny: number
}
