<template>
  <div class="ai-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h2>智能分析</h2>
      <div class="actions">
        <el-select v-model="months" size="default" style="width: 120px; margin-right: 12px;">
          <el-option :value="1" label="近 1 个月" />
          <el-option :value="3" label="近 3 个月" />
          <el-option :value="6" label="近 6 个月" />
          <el-option :value="12" label="近 12 个月" />
        </el-select>
        <el-button type="primary" :loading="aiStore.adviceLoading" @click="handleGenerate">
          <el-icon><MagicStick /></el-icon> 生成分析
        </el-button>
      </div>
    </div>

    <!-- Tabs -->
    <el-tabs v-model="activeTab" class="ai-tabs">
      <!-- Tab 1: 智能建议 -->
      <el-tab-pane label="智能建议" name="advice">
        <div v-if="aiStore.adviceLoading" style="padding: 40px 0;">
          <el-skeleton :rows="8" animated />
        </div>

        <el-empty v-else-if="!aiStore.currentAdvice" description="暂无分析数据，点击上方按钮生成">
          <el-button type="primary" @click="handleGenerate">立即生成</el-button>
        </el-empty>

        <template v-else>
          <!-- 元信息 -->
          <div class="meta-bar">
            <span class="meta-text">
              分析周期：{{ periodLabel }}
            </span>
            <span class="meta-text">
              生成时间：{{ generatedAtLabel }}
            </span>
            <el-tag v-if="aiStore.currentAdvice.from_cache" size="small" type="info">缓存结果</el-tag>
            <el-tag v-else size="small" type="success">新生成</el-tag>
          </div>

          <!-- 三列建议卡片 -->
          <el-row :gutter="16">
            <el-col :span="8" :xs="24" :sm="24" :md="8">
              <AIAdviceCard
                title="消费亮点"
                type="highlight"
                :items="aiStore.currentAdvice.advice.highlights ?? []"
              />
            </el-col>
            <el-col :span="8" :xs="24" :sm="24" :md="8">
              <AIAdviceCard
                title="风险提醒"
                type="warning"
                :items="aiStore.currentAdvice.advice.warnings ?? []"
              />
            </el-col>
            <el-col :span="8" :xs="24" :sm="24" :md="8">
              <AIAdviceCard
                title="优化建议"
                type="suggestion"
                :items="aiStore.currentAdvice.advice.suggestions ?? []"
              />
            </el-col>
          </el-row>

          <!-- 预算建议 -->
          <el-card shadow="hover" class="budget-card">
            <template #header>
              <div class="card-header">
                <span>下月预算建议</span>
                <span class="budget-total">总计：¥{{ totalBudget }}</span>
              </div>
            </template>
            <AIBudgetChart
              :breakdown="budgetBreakdown"
              :total="totalBudget"
            />
          </el-card>

          <!-- 完整报告 -->
          <el-card shadow="hover" class="report-card">
            <el-collapse>
              <el-collapse-item title="查看完整分析报告" name="report">
                <pre class="report-content">{{ aiStore.currentAdvice.advice.full_report }}</pre>
              </el-collapse-item>
            </el-collapse>
          </el-card>
        </template>
      </el-tab-pane>

      <!-- Tab 2: 历史记录 -->
      <el-tab-pane label="历史记录" name="history">
        <el-table
          :data="aiStore.historyRecords"
          v-loading="aiStore.historyLoading"
          stripe
          style="width: 100%"
        >
          <el-table-column prop="generated_at" label="生成时间" width="180">
            <template #default="{ row }">
              {{ formatTime(row.generated_at) }}
            </template>
          </el-table-column>
          <el-table-column label="分析周期" width="240">
            <template #default="{ row }">
              {{ formatTime(row.analysis_period?.start) }} ~ {{ formatTime(row.analysis_period?.end) }}
            </template>
          </el-table-column>
          <el-table-column prop="summary" label="摘要" show-overflow-tooltip />
          <el-table-column label="操作" width="100" align="center">
            <template #default="{ row }">
              <el-button link type="primary" @click="viewDetail(row.id)">查看</el-button>
            </template>
          </el-table-column>
        </el-table>

        <div class="pagination-wrap" v-if="aiStore.historyTotal > 0">
          <el-pagination
            v-model:current-page="historyPage"
            v-model:page-size="historyPageSize"
            :page-sizes="[10, 20, 50]"
            background
            layout="total, sizes, prev, pager, next"
            :total="aiStore.historyTotal"
            @size-change="handleHistorySizeChange"
            @current-change="handleHistoryPageChange"
          />
        </div>

        <!-- 详情抽屉 -->
        <el-drawer v-model="drawerVisible" title="建议详情" size="50%">
          <div v-if="aiStore.historyDetailLoading" v-loading="true" style="height: 200px" />
          <template v-else-if="aiStore.historyDetail">
            <div class="drawer-section">
              <AIAdviceCard title="消费亮点" type="highlight" :items="aiStore.historyDetail.advice.highlights ?? []" />
            </div>
            <div class="drawer-section">
              <AIAdviceCard title="风险提醒" type="warning" :items="aiStore.historyDetail.advice.warnings ?? []" />
            </div>
            <div class="drawer-section">
              <AIAdviceCard title="优化建议" type="suggestion" :items="aiStore.historyDetail.advice.suggestions ?? []" />
            </div>
            <el-divider />
            <h4 style="margin: 0 0 12px; color: #111827;">完整报告</h4>
            <pre class="report-content">{{ aiStore.historyDetail.advice.full_report }}</pre>
          </template>
        </el-drawer>
      </el-tab-pane>

      <!-- Tab 3: 用量统计 -->
      <el-tab-pane label="用量统计" name="usage">
        <div v-loading="aiStore.usageLoading">
          <el-row :gutter="20" v-if="aiStore.usage">
            <el-col :span="6" :xs="12" :sm="8" :md="6">
              <el-card shadow="hover" class="stat-card">
                <div class="stat-title">分类调用次数</div>
                <div class="stat-value">{{ aiStore.usage.classify_calls }}</div>
                <div class="stat-desc">本月累计</div>
              </el-card>
            </el-col>
            <el-col :span="6" :xs="12" :sm="8" :md="6">
              <el-card shadow="hover" class="stat-card">
                <div class="stat-title">建议生成次数</div>
                <div class="stat-value">{{ aiStore.usage.advice_calls }}</div>
                <div class="stat-desc">本月累计</div>
              </el-card>
            </el-col>
            <el-col :span="6" :xs="12" :sm="8" :md="6">
              <el-card shadow="hover" class="stat-card">
                <div class="stat-title">Token 消耗</div>
                <div class="stat-value">{{ aiStore.usage.total_tokens_used.toLocaleString() }}</div>
                <div class="stat-desc">{{ aiStore.usage.month }}</div>
              </el-card>
            </el-col>
            <el-col :span="6" :xs="12" :sm="8" :md="6">
              <el-card shadow="hover" class="stat-card">
                <div class="stat-title">预估费用</div>
                <div class="stat-value">¥{{ aiStore.usage.estimated_cost_cny?.toFixed(2) ?? '0.00' }}</div>
                <div class="stat-desc">本月累计</div>
              </el-card>
            </el-col>
          </el-row>
          <el-empty v-else description="暂无用量数据" />
        </div>
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { MagicStick } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import { useAIStore } from '@/stores/ai'
import AIAdviceCard from '@/components/business/AIAdviceCard.vue'
import AIBudgetChart from '@/components/business/AIBudgetChart.vue'

const aiStore = useAIStore()
const activeTab = ref('advice')
const months = ref(3)

// ─── 建议相关 ────────────────────────────────
const handleGenerate = () => aiStore.fetchAdvice(months.value, true)

const periodLabel = computed(() => {
  if (!aiStore.currentAdvice?.analysis_period) return ''
  const p = aiStore.currentAdvice.analysis_period
  return `${dayjs(p.start).format('YYYY-MM-DD')} ~ ${dayjs(p.end).format('YYYY-MM-DD')}`
})

const generatedAtLabel = computed(() => {
  if (!aiStore.currentAdvice?.generated_at) return ''
  return dayjs(aiStore.currentAdvice.generated_at).format('YYYY-MM-DD HH:mm:ss')
})

const budgetBreakdown = computed(() =>
  aiStore.currentAdvice?.advice.next_month_budget?.breakdown ?? []
)

const totalBudget = computed(() =>
  aiStore.currentAdvice?.advice.next_month_budget?.total ?? 0
)

// ─── 历史记录 ────────────────────────────────
const historyPage = ref(1)
const historyPageSize = ref(10)
const drawerVisible = ref(false)

const viewDetail = async (id: number) => {
  drawerVisible.value = true
  await aiStore.fetchHistoryDetail(id)
}

const handleHistoryPageChange = (p: number) => {
  historyPage.value = p
  aiStore.fetchHistory(p, historyPageSize.value)
}

const handleHistorySizeChange = (s: number) => {
  historyPageSize.value = s
  aiStore.fetchHistory(historyPage.value, s)
}

const formatTime = (t: string | undefined) => {
  if (!t) return '-'
  return dayjs(t).format('YYYY-MM-DD')
}

// ─── Tab 切换懒加载 ────────────────────────────────
watch(activeTab, (tab) => {
  if (tab === 'history' && aiStore.historyRecords.length === 0) aiStore.fetchHistory()
  if (tab === 'usage' && !aiStore.usage) aiStore.fetchUsage()
})

onMounted(() => {
  aiStore.fetchAdvice()
})
</script>

<style scoped>
.ai-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: #111827;
}

.actions {
  display: flex;
  align-items: center;
}

.meta-bar {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 12px 16px;
  background: #f9fafb;
  border-radius: 8px;
  font-size: 13px;
  color: #6b7280;
}

.budget-card {
  border-radius: 12px;
  border: 1px solid #e5e7eb;
}

.budget-total {
  font-size: 16px;
  font-weight: 600;
  color: #16A34A;
}

.report-card {
  border-radius: 12px;
  border: 1px solid #e5e7eb;
}

.report-content {
  font-size: 14px;
  color: #374151;
  line-height: 1.8;
  white-space: pre-wrap;
  word-wrap: break-word;
  margin: 0;
  font-family: inherit;
}

.pagination-wrap {
  display: flex;
  justify-content: flex-end;
  padding: 16px 0;
}

.drawer-section {
  margin-bottom: 16px;
}

.stat-card {
  border-radius: 12px;
  border: 1px solid #e5e7eb;
  text-align: center;
  padding: 8px 0;
}

.stat-title {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 12px;
}

.stat-value {
  font-size: 28px;
  font-weight: 700;
  color: #111827;
  margin-bottom: 8px;
}

.stat-desc {
  font-size: 12px;
  color: #9ca3af;
}

/* Element Plus 绿色主题覆盖 */
:deep(.el-button--primary) {
  --el-button-bg-color: #16A34A;
  --el-button-border-color: #16A34A;
  --el-button-hover-bg-color: #15803D;
  --el-button-hover-border-color: #15803D;
  --el-button-active-bg-color: #166534;
  --el-button-active-border-color: #166534;
}

:deep(.el-tabs__active-bar) {
  background-color: #16A34A;
}

:deep(.el-tabs__item.is-active) {
  color: #16A34A;
}

:deep(.el-tabs__item:hover) {
  color: #16A34A;
}

:deep(.el-pagination.is-background .el-pager li.is-active) {
  background-color: #16A34A;
}
</style>
