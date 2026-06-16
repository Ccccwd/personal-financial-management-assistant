<template>
  <el-card shadow="hover" class="ai-insight-card">
    <template #header>
      <div class="card-header">
        <span class="card-title">✦ 智能洞察</span>
        <el-button link type="primary" size="small" @click="$router.push('/ai')">
          查看详情 <el-icon><ArrowRight /></el-icon>
        </el-button>
      </div>
    </template>
    <div v-if="loading" v-loading="true" style="height: 80px" />
    <div v-else-if="insights.length > 0" class="insight-list">
      <div v-for="(item, idx) in insights" :key="idx" class="insight-item">
        <span :class="['insight-dot', `insight-dot--${item.type}`]"></span>
        <span class="insight-text">{{ item.text }}</span>
      </div>
    </div>
    <div v-else class="insight-empty">
      <span class="empty-text">暂无智能分析</span>
      <el-button size="small" type="primary" @click="$router.push('/ai')">
        生成首次分析
      </el-button>
    </div>
  </el-card>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ArrowRight } from '@element-plus/icons-vue'
import { getAIAdvice } from '@/api/ai'
import type { AIAdviceResponse } from '@/types/ai'

interface InsightItem {
  type: 'highlight' | 'warning'
  text: string
}

const loading = ref(false)
const insights = ref<InsightItem[]>([])

onMounted(async () => {
  loading.value = true
  try {
    const res = await getAIAdvice({ months: 3, force_refresh: false })
    const data = res as unknown as AIAdviceResponse
    if (data?.advice) {
      const items: InsightItem[] = []
      data.advice.highlights?.slice(0, 2).forEach(t => items.push({ type: 'highlight', text: t }))
      data.advice.warnings?.slice(0, 1).forEach(t => items.push({ type: 'warning', text: t }))
      insights.value = items.slice(0, 3)
    }
  } catch {
    // 拦截器已处理
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.ai-insight-card {
  border-radius: 12px;
  border: 1px solid #e5e7eb;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  color: #111827;
}

.insight-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.insight-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  font-size: 14px;
  color: #374151;
  line-height: 1.5;
}

.insight-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  margin-top: 8px;
  flex-shrink: 0;
}

.insight-dot--highlight { background: #16A34A; }
.insight-dot--warning { background: #F59E0B; }

.insight-empty {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.empty-text {
  font-size: 14px;
  color: #9ca3af;
}

:deep(.el-button--primary) {
  --el-button-bg-color: #16A34A;
  --el-button-border-color: #16A34A;
  --el-button-hover-bg-color: #15803D;
  --el-button-hover-border-color: #15803D;
}
</style>
