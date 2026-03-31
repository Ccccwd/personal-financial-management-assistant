import request from '@/utils/request'
import {
  ReportMonthly,
  ReportYearly,
  APIResponse
} from '@/types/index'

/**
 * 获取月度报告
 * @param year 年份
 * @param month 月份
 */
export function getMonthlyReport(year: number, month: number) {
  return request.get<ReportMonthly>('/reports/monthly', { params: { year, month } })
}

/**
 * 获取年度报告
 * @param year 年份
 */
export function getYearlyReport(year: number) {
  return request.get<ReportYearly>('/reports/yearly', { params: { year } })
}

/**
 * 获取分类分析报告
 * @param categoryId 分类ID
 * @param days 分析天数
 */
export function getCategoryReport(categoryId: number, days: number = 30) {
  return request.get<any>(`/reports/category/${categoryId}`, { params: { days } })
}

/**
 * 生成并发送月度自动报告
 */
export function generateMonthlyAutoReport() {
  return request.post<{ success: boolean; task_id: string }>('/reports/monthly-auto-report')
}
