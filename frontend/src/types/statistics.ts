export interface StatisticsOverview {
  total_assets: number
  monthly_income: number
  monthly_expense: number
  daily_average_expense: number
  budget_usage_percent: number
}

export interface TrendDataPoint {
  date: string // or week/month label
  income: number
  expense: number
  balance: number
}

export interface CategoryStatItem {
  category_id: number
  category_name: string
  amount: number
  percent: number
  transaction_count: number
  color?: string
  icon?: string
}

export interface ExportRequest {
  transaction_type?: 'all' | 'income' | 'expense'
  start_date: string
  end_date: string
}
