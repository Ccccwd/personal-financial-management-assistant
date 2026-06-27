import request from '@/api/request'
import {
  AIAdviceDetail,
  AIAdviceHistoryPayload,
  AIAdviceResponse,
  AIUsage,
} from '@/types/index'

const AI_ADVICE_TIMEOUT = 120000

/**
 * 获取个性化理财建议
 * @param params 查询参数
 */
export function getAIAdvice(params?: {
  months?: number
  force_refresh?: boolean
}) {
  return request.get<AIAdviceResponse>('/ai/advice', { params, timeout: AI_ADVICE_TIMEOUT })
}

/**
 * 获取历史建议记录列表
 * @param params 查询参数
 */
export function getAIAdviceHistory(params?: {
  page?: number
  page_size?: number
}) {
  return request.get<AIAdviceHistoryPayload>('/ai/advice/history', { params })
}

/**
 * 获取历史建议详情
 * @param recordId 记录ID
 */
export function getAIAdviceDetail(recordId: number) {
  return request.get<AIAdviceDetail>(`/ai/advice/history/${recordId}`)
}

/**
 * 获取 AI 服务用量统计
 */
export function getAIUsage() {
  return request.get<AIUsage>('/ai/usage')
}
