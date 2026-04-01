import request from '@/utils/request'
import {
  AIClassifyItem,
  AIClassifyResponse,
  AIAdviceHistoryPayload,
  AIAdviceResponse,
  AIUsage,
  ReclassifyResponse
} from '@/types/index'

/**
 * 账单智能分类
 * @param items 待分类条目列表
 */
export function aiClassify(items: AIClassifyItem[]) {
  return request.post<AIClassifyResponse>('/ai/classify', { items })
}

/**
 * 重新分类单条交易
 * @param transactionId 交易ID
 * @param dryRun 是否仅预览
 */
export function reclassifyTransaction(transactionId: number, dryRun: boolean = false) {
  return request.post<ReclassifyResponse>(`/ai/reclassify/${transactionId}`, null, {
    params: { dry_run: dryRun }
  })
}

/**
 * 获取个性化理财建议
 * @param params 查询参数
 */
export function getAIAdvice(params?: {
  months?: number
  force_refresh?: boolean
}) {
  return request.get<AIAdviceResponse>('/ai/advice', { params })
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
  return request.get<AIAdviceResponse>(`/ai/advice/history/${recordId}`)
}

/**
 * 获取 AI 服务用量统计
 */
export function getAIUsage() {
  return request.get<AIUsage>('/ai/usage')
}
