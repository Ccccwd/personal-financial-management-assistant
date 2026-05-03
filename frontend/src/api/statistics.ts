import request from '@/api/request'
import {
  CategoryStatisticsResponse,
  ExportExcelResponse,
  StatisticsOverview,
  TrendResponse,
  ExportRequest
} from '@/types/index'

/**
 * 获取首页概览
 * @param params 查询参数
 */
export function getStatisticsOverview(params?: {
  current_year?: number
  current_month?: number
}) {
  // 前端使用 Mock 数据进行开发测试
  // return request.get<StatisticsOverview>('/statistics/overview', { params })
  
  return Promise.resolve({
    monthly_summary: {
      income: 12580.50,
      expense: 3450.20,
      balance: 9130.30,
      income_growth: 12.5,
      expense_growth: -5.2
    },
    total_balance: 56780.00,
    category_distribution: [
      { name: '餐饮美食', icon: 'Food', color: '#10B981', amount: 1200, percentage: 34.7 },
      { name: '交通出行', icon: 'Car', color: '#3B82F6', amount: 500, percentage: 14.4 },
      { name: '住房物业', icon: 'House', color: '#8B5CF6', amount: 1500, percentage: 43.4 },
      { name: '休闲娱乐', icon: 'Ticket', color: '#F59E0B', amount: 250.2, percentage: 7.2 }
    ],
    trend_data: [
      { date: '2026-04-04', income: 0, expense: 120 },
      { date: '2026-04-05', income: 0, expense: 45 },
      { date: '2026-04-06', income: 8000, expense: 300 },
      { date: '2026-04-07', income: 0, expense: 150 },
      { date: '2026-04-08', income: 200, expense: 80 },
      { date: '2026-04-09', income: 0, expense: 400 },
      { date: '2026-04-10', income: 0, expense: 200 }
    ],
    period: `${params?.current_year || new Date().getFullYear()}年${params?.current_month || new Date().getMonth() + 1}月`
  } as unknown as StatisticsOverview);
}

/**
 * 获取趋势数据
 * @param params 查询参数
 */
export function getTrendData(params?: {
  period?: 'daily' | 'weekly' | 'monthly' | 'yearly'
  start_date?: string
  end_date?: string
}) {
  return request.get<TrendResponse>('/statistics/trend', { params })
}

/**
 * 获取分类统计
 * @param params 查询参数
 */
export function getCategoryStatistics(params: {
  transaction_type?: 'expense' | 'income'
  period?: 'monthly' | 'yearly'
  year: number
  month?: number
}) {
  return request.get<CategoryStatisticsResponse>('/statistics/category', { params })
}

/**
 * 导出 Excel
 * @param params 导出参数
 */
export function exportExcel(params: ExportRequest) {
  return request.get<ExportExcelResponse>('/statistics/export/excel', { params })
}
