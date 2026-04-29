
export interface ReportMonthly {
  year: number
  month: number
  total_income: number
  total_expense: number
  net_saving: number
  top_expense_categories: any[] // Reuse CategoryStatItem if needed
  daily_trend: any[]
  budget_analysis: any
  advice: string
}

export interface ReportYearly {
  year: number
  total_income: number
  total_expense: number
  net_saving: number
  monthly_trend: any[]
  top_expense_categories: any[]
}

export interface CategoryReport {
  category_id: number
  days: number
  [key: string]: unknown
}

export interface MonthlyAutoReportResponse {
  success?: boolean
  task_id?: string
  message?: string
}
