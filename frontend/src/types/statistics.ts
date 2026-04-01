export interface MonthlySummary {
  income: number
  expense: number
  balance: number
  income_growth: number
  expense_growth: number
}

export interface CategoryDistribution {
  name: string
  icon?: string
  color?: string
  amount: number
  percentage: number
}

export interface StatisticsOverview {
  period: string
  monthly_summary: MonthlySummary
  total_balance: number
  category_distribution: CategoryDistribution[]
  trend_data: TrendDataPoint[]
}

export interface TrendDataPoint {
  date: string
  income?: number
  expense?: number
  balance?: number
  amount?: number
}

export interface CategoryStatItem {
  id: number
  name: string
  icon?: string
  color?: string
  amount: number
  count: number
  percentage: number
}

export interface ExportRequest {
  transaction_type?: 'all' | 'income' | 'expense'
  start_date: string
  end_date: string
}

export interface TrendResponse {
  period: 'daily' | 'weekly' | 'monthly' | 'yearly'
  start_date: string
  end_date: string
  trend: TrendDataPoint[]
}

export interface CategoryStatisticsResponse {
  transaction_type: 'expense' | 'income'
  total_amount: number
  categories: CategoryStatItem[]
}

export interface ExportExcelResponse {
  file_path: string
  file_name: string
  download_url?: string
}
