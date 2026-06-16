import { defineStore } from 'pinia'
import { ref } from 'vue'
import {
  getAIAdvice,
  getAIAdviceHistory,
  getAIAdviceDetail,
  getAIUsage,
  reclassifyTransaction
} from '@/api/ai'
import type {
  AIAdviceResponse,
  AIAdviceHistoryPayload,
  AIAdviceHistoryItem,
  AIAdviceDetail,
  AIUsage,
  ReclassifyResponse
} from '@/types/ai'

/** 将历史详情接口的扁平结构规范为页面使用的 advice 结构 */
function normalizeAdviceDetail(detail: AIAdviceDetail): AIAdviceResponse {
  const breakdown = detail.next_month_budget?.breakdown ?? []
  const total = detail.next_month_budget?.total ?? breakdown.reduce(
    (sum, item) => sum + Number(item.suggested_amount || 0),
    0
  )
  return {
    generated_at: detail.created_at,
    from_cache: true,
    analysis_period: detail.analysis_period,
    advice: {
      highlights: detail.highlights ?? [],
      warnings: detail.warnings ?? [],
      suggestions: detail.suggestions ?? [],
      next_month_budget: { total, breakdown },
      full_report: detail.full_report ?? '',
    },
  }
}

export const useAIStore = defineStore('ai', () => {
  const currentAdvice = ref<AIAdviceResponse | null>(null)
  const adviceLoading = ref(false)

  const fetchAdvice = async (months: number = 3, forceRefresh: boolean = false) => {
    adviceLoading.value = true
    try {
      const res = await getAIAdvice({ months, force_refresh: forceRefresh })
      currentAdvice.value = res as unknown as AIAdviceResponse
    } catch {
      // 拦截器已处理错误提示
    } finally {
      adviceLoading.value = false
    }
  }

  const historyRecords = ref<AIAdviceHistoryItem[]>([])
  const historyTotal = ref(0)
  const historyLoading = ref(false)

  const fetchHistory = async (page: number = 1, pageSize: number = 10) => {
    historyLoading.value = true
    try {
      const res = await getAIAdviceHistory({ page, page_size: pageSize })
      const payload = res as unknown as AIAdviceHistoryPayload
      historyRecords.value = payload?.items ?? []
      historyTotal.value = payload?.total ?? 0
    } catch {
      historyRecords.value = []
      historyTotal.value = 0
    } finally {
      historyLoading.value = false
    }
  }

  const historyDetail = ref<AIAdviceResponse | null>(null)
  const historyDetailLoading = ref(false)

  const fetchHistoryDetail = async (recordId: number) => {
    historyDetailLoading.value = true
    try {
      const res = await getAIAdviceDetail(recordId)
      historyDetail.value = normalizeAdviceDetail(res as unknown as AIAdviceDetail)
    } catch {
      historyDetail.value = null
    } finally {
      historyDetailLoading.value = false
    }
  }

  const usage = ref<AIUsage | null>(null)
  const usageLoading = ref(false)

  const fetchUsage = async () => {
    usageLoading.value = true
    try {
      const res = await getAIUsage()
      usage.value = res as unknown as AIUsage
    } catch {
      usage.value = null
    } finally {
      usageLoading.value = false
    }
  }

  const reclassifyLoading = ref(false)

  const reclassify = async (transactionId: number, dryRun: boolean = false) => {
    reclassifyLoading.value = true
    try {
      const res = await reclassifyTransaction(transactionId, dryRun)
      return res as unknown as ReclassifyResponse
    } catch {
      return null
    } finally {
      reclassifyLoading.value = false
    }
  }

  return {
    currentAdvice, adviceLoading, fetchAdvice,
    historyRecords, historyTotal, historyLoading, fetchHistory,
    historyDetail, historyDetailLoading, fetchHistoryDetail,
    usage, usageLoading, fetchUsage,
    reclassifyLoading, reclassify
  }
})
