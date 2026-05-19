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
  return request.get<StatisticsOverview>('/statistics/overview', { params })
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
