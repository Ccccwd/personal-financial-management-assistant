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
  AIUsage,
  ReclassifyResponse
} from '@/types/ai'

export const useAIStore = defineStore('ai', () => {
  // ─── 当前建议 ────────────────────────────────
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

  // ─── 历史记录 ────────────────────────────────
  const historyRecords = ref<AIAdviceHistoryItem[]>([])
  const historyTotal = ref(0)
  const historyLoading = ref(false)

  const fetchHistory = async (page: number = 1, pageSize: number = 10) => {
    historyLoading.value = true
    try {
      const res = await getAIAdviceHistory({ page, page_size: pageSize })
      const payload = res as unknown as AIAdviceHistoryPayload
      historyRecords.value = payload?.records ?? []
      historyTotal.value = payload?.total ?? 0
    } catch {
      historyRecords.value = []
      historyTotal.value = 0
    } finally {
      historyLoading.value = false
    }
  }

  // ─── 历史详情 ────────────────────────────────
  const historyDetail = ref<AIAdviceResponse | null>(null)
  const historyDetailLoading = ref(false)

  const fetchHistoryDetail = async (recordId: number) => {
    historyDetailLoading.value = true
    try {
      const res = await getAIAdviceDetail(recordId)
      historyDetail.value = res as unknown as AIAdviceResponse
    } catch {
      historyDetail.value = null
    } finally {
      historyDetailLoading.value = false
    }
  }

  // ─── 用量统计 ────────────────────────────────
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

  // ─── 重新分类 ────────────────────────────────
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
