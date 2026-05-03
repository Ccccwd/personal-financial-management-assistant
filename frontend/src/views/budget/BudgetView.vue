<template>
  <div class="budget-page">
    <!-- 页面标题 -->
    <div class="page-header">
      <h1 class="page-title">预算管理</h1>
      <div class="header-actions">
        <el-button @click="fetchData">
          <el-icon><Refresh /></el-icon>刷新
        </el-button>
        <el-button type="primary" @click="openAddDialog">
          <el-icon><Plus /></el-icon>添加预算
        </el-button>
      </div>
    </div>

    <!-- 筛选条件 -->
    <el-card shadow="never" class="filter-card">
      <el-form :inline="true" class="filter-form">
        <el-form-item label="年份">
          <el-select v-model="queryForm.year" style="width: 120px" @change="fetchData">
            <el-option
              v-for="y in availableYears"
              :key="y"
              :label="`${y}年`"
              :value="y"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="月份">
          <el-select
            v-model="queryForm.month"
            placeholder="全年"
            clearable
            style="width: 110px"
            @change="fetchData"
          >
            <el-option v-for="m in 12" :key="m" :label="`${m}月`" :value="m" />
          </el-select>
        </el-form-item>
        <el-form-item label="周期类型">
          <el-select
            v-model="queryForm.period_type"
            placeholder="全部"
            clearable
            style="width: 130px"
            @change="fetchData"
          >
            <el-option label="月度预算" value="monthly" />
            <el-option label="年度预算" value="yearly" />
          </el-select>
        </el-form-item>
      </el-form>
    </el-card>

    <!-- 预算汇总卡片 -->
    <el-card shadow="never" class="summary-card" v-loading="loading">
      <div class="summary-header">
        <h3 class="summary-title">预算汇总</h3>
        <el-tag
          :type="overallTag.type"
          effect="plain"
          class="overall-tag"
        >
          {{ overallTag.text }}
        </el-tag>
      </div>
      <div class="summary-stats">
        <div class="stat-item">
          <div class="stat-label">总预算</div>
          <div class="stat-value">¥{{ summaryTotal.toLocaleString('zh-CN', { minimumFractionDigits: 2 }) }}</div>
        </div>
        <div class="stat-divider" />
        <div class="stat-item">
          <div class="stat-label">已使用</div>
          <div class="stat-value stat-used">¥{{ summaryUsed.toLocaleString('zh-CN', { minimumFractionDigits: 2 }) }}</div>
        </div>
        <div class="stat-divider" />
        <div class="stat-item">
          <div class="stat-label">剩余</div>
          <div class="stat-value" :class="summaryRemaining < 0 ? 'stat-exceeded' : 'stat-remaining'">
            ¥{{ Math.abs(summaryRemaining).toLocaleString('zh-CN', { minimumFractionDigits: 2 }) }}
            <span v-if="summaryRemaining < 0" class="exceeded-label">超支</span>
          </div>
        </div>
        <div class="stat-divider" />
        <div class="stat-item">
          <div class="stat-label">使用率</div>
          <div class="stat-value">{{ summaryRate }}%</div>
        </div>
      </div>
      <el-progress
        :percentage="Math.min(summaryRate, 100)"
        :color="getProgressColor(summaryRate)"
        :stroke-width="10"
        :show-text="false"
        class="summary-progress"
      />
    </el-card>

    <!-- 状态概览 -->
    <div class="status-bar" v-if="!loading && budgets.length > 0">
      <span class="status-legend">
        <i class="dot dot-normal" />正常：{{ normalCount }}
      </span>
      <span class="status-legend">
        <i class="dot dot-warning" />预警：{{ warningCount }}
      </span>
      <span class="status-legend">
        <i class="dot dot-exceeded" />超支：{{ exceededCount }}
      </span>
    </div>

    <!-- 分类预算列表 -->
    <div v-if="loading" v-loading="true" class="loading-placeholder" />
    <div v-else-if="budgets.length > 0" class="budget-grid">
      <el-card
        v-for="item in budgets"
        :key="item.id"
        shadow="hover"
        class="budget-card"
        :class="`status-${item.status}`"
      >
        <!-- 卡片头部 -->
        <div class="card-header">
          <div class="card-category">
            <span class="cat-icon">{{ item.category?.icon || '💰' }}</span>
            <div class="cat-info">
              <div class="cat-name">{{ item.category?.name || '总预算' }}</div>
              <div class="cat-period">{{ getPeriodText(item) }}</div>
            </div>
          </div>
          <div class="card-actions">
            <el-tag
              :type="statusTag(item.status).type"
              size="small"
              effect="light"
              class="status-tag"
            >
              {{ statusTag(item.status).text }}
            </el-tag>
            <el-button link type="primary" size="small" @click="openEditDialog(item)">
              编辑
            </el-button>
            <el-popconfirm
              title="确定要删除此预算吗？"
              confirm-button-text="确定"
              cancel-button-text="取消"
              @confirm="handleDelete(item.id)"
            >
              <template #reference>
                <el-button link type="danger" size="small">删除</el-button>
              </template>
            </el-popconfirm>
          </div>
        </div>

        <!-- 金额信息 -->
        <div class="card-amounts">
          <span class="amount-used">已用 ¥{{ Number(item.actual_spending).toLocaleString('zh-CN', { minimumFractionDigits: 2 }) }}</span>
          <span class="amount-sep">/</span>
          <span class="amount-total">¥{{ Number(item.amount).toLocaleString('zh-CN', { minimumFractionDigits: 2 }) }}</span>
        </div>

        <!-- 进度条 -->
        <el-progress
          :percentage="Math.min(item.percentage, 100)"
          :color="getProgressColor(item.percentage)"
          :stroke-width="8"
          :show-text="false"
          class="card-progress"
        />

        <!-- 进度信息行 -->
        <div class="card-footer">
          <span :style="{ color: getProgressColor(item.percentage) }" class="rate-text">
            {{ item.percentage }}%
          </span>
          <span v-if="item.status === 'exceeded'" class="exceeded-info">
            超支 ¥{{ Math.abs(item.remaining).toLocaleString('zh-CN', { minimumFractionDigits: 2 }) }}
          </span>
          <span v-else class="remaining-info">
            剩余 ¥{{ Number(item.remaining).toLocaleString('zh-CN', { minimumFractionDigits: 2 }) }}
          </span>
        </div>
      </el-card>
    </div>
    <el-empty
      v-else
        description="当前条件下暂无预算，点击「添加预算」开始设置"
      class="empty-state"
    >
      <el-button type="primary" @click="openAddDialog">添加预算</el-button>
    </el-empty>

    <!-- 添加/编辑对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogForm.id ? '编辑预算' : '添加预算'"
      width="460px"
      destroy-on-close
      align-center
    >
      <el-form
        ref="formRef"
        :model="dialogForm"
        :rules="dialogRules"
        label-width="90px"
        class="dialog-form"
      >
        <el-form-item label="周期类型" prop="period_type">
          <el-select
            v-model="dialogForm.period_type"
            placeholder="请选择"
            style="width: 100%"
            @change="handlePeriodTypeChange"
          >
            <el-option label="月度预算" value="monthly" />
            <el-option label="年度预算" value="yearly" />
          </el-select>
        </el-form-item>

        <el-form-item label="年份" prop="year">
          <el-select v-model="dialogForm.year" style="width: 100%">
            <el-option
              v-for="y in availableYears"
              :key="y"
              :label="`${y}年`"
              :value="y"
            />
          </el-select>
        </el-form-item>

        <el-form-item
          v-if="dialogForm.period_type === 'monthly'"
          label="月份"
          prop="month"
        >
          <el-select v-model="dialogForm.month" placeholder="请选择月份" style="width: 100%">
            <el-option v-for="m in 12" :key="m" :label="`${m}月`" :value="m" />
          </el-select>
        </el-form-item>

        <el-form-item label="关联分类">
          <el-select
            v-model="dialogForm.category_id"
            placeholder="不选则为总体预算"
            clearable
            style="width: 100%"
            :loading="categoryLoading"
          >
            <el-option
              v-for="cat in expenseCategories"
              :key="cat.id"
              :value="cat.id"
            >
              <span class="cat-option">
                <span>{{ cat.icon || '📝' }}</span>
                <span>{{ cat.name }}</span>
              </span>
            </el-option>
            <template #label="{ value }">
              <span v-if="value">
                {{ expenseCategories.find(c => c.id === value)?.icon || '📝' }}
                {{ expenseCategories.find(c => c.id === value)?.name }}
              </span>
              <span v-else style="color: #9ca3af">不选则为总体预算</span>
            </template>
          </el-select>
        </el-form-item>

        <el-form-item label="预算金额" prop="amount">
          <el-input-number
            v-model="dialogForm.amount"
            :min="0.01"
            :precision="2"
            :step="100"
            style="width: 100%"
            placeholder="请输入预算金额"
          />
        </el-form-item>

        <el-form-item label="预警阈值">
          <div class="threshold-row">
            <el-slider
              v-model="dialogForm.alert_threshold"
              :step="5"
              :min="50"
              :max="100"
              style="flex: 1"
            />
            <span class="threshold-label">{{ dialogForm.alert_threshold }}%</span>
          </div>
          <div class="threshold-tip">
            使用率达到 {{ dialogForm.alert_threshold }}% 时触发预警提示
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">
          {{ dialogForm.id ? '保存修改' : '创建预算' }}
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch } from 'vue'
import { Plus, Refresh } from '@element-plus/icons-vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import dayjs from 'dayjs'
import { getBudgets, createBudget, updateBudget, deleteBudget } from '@/api/budgets'
import { getCategories } from '@/api/categories'
import type { BudgetWithProgress, BudgetPeriodType } from '@/types/budget'
import type { Category } from '@/types/category'

// ─── 状态 ───────────────────────────────────────────────────────────────────
const loading = ref(false)
const submitting = ref(false)
const dialogVisible = ref(false)
const categoryLoading = ref(false)

const formRef = ref<FormInstance>()

// ─── 数据 ───────────────────────────────────────────────────────────────────
const budgets = ref<BudgetWithProgress[]>([])
const expenseCategories = ref<Category[]>([])

// ─── 筛选 ───────────────────────────────────────────────────────────────────
const currentYear = dayjs().year()
const currentMonth = dayjs().month() + 1

const queryForm = reactive({
  year: currentYear,
  month: currentMonth as number | undefined,
  period_type: 'monthly' as BudgetPeriodType | undefined,
})

const availableYears = computed(() => {
  return Array.from({ length: 5 }, (_, i) => currentYear - i + 1)
})

// ─── 对话框表单 ─────────────────────────────────────────────────────────────
const dialogForm = reactive({
  id: 0,
  period_type: 'monthly' as BudgetPeriodType,
  year: currentYear,
  month: currentMonth as number | undefined,
  category_id: null as number | null,
  amount: 1000,
  alert_threshold: 80,
})

const dialogRules: FormRules = {
  period_type: [{ required: true, message: '请选择周期类型', trigger: 'change' }],
  year: [{ required: true, message: '请选择年份', trigger: 'change' }],
  month: [
    {
      required: true,
      message: '请选择月份',
      trigger: 'change',
      validator: (_rule, _value, callback) => {
        if (dialogForm.period_type === 'monthly' && !dialogForm.month) {
          callback(new Error('月度预算必须选择月份'))
        } else {
          callback()
        }
      },
    },
  ],
  amount: [
    { required: true, message: '请输入预算金额', trigger: 'blur' },
    {
      validator: (_rule, value, callback) => {
        if (value <= 0) {
          callback(new Error('预算金额必须大于 0'))
        } else {
          callback()
        }
      },
      trigger: 'blur',
    },
  ],
}

// ─── 汇总计算 ────────────────────────────────────────────────────────────────
const summaryTotal = computed(() =>
  budgets.value.reduce((sum, b) => sum + Number(b.amount), 0)
)
const summaryUsed = computed(() =>
  budgets.value.reduce((sum, b) => sum + Number(b.actual_spending), 0)
)
const summaryRemaining = computed(() => summaryTotal.value - summaryUsed.value)
const summaryRate = computed(() => {
  if (summaryTotal.value === 0) return 0
  return Math.round((summaryUsed.value / summaryTotal.value) * 100)
})

const normalCount = computed(() => budgets.value.filter(b => b.status === 'normal').length)
const warningCount = computed(() => budgets.value.filter(b => b.status === 'warning').length)
const exceededCount = computed(() => budgets.value.filter(b => b.status === 'exceeded').length)

const overallTag = computed(() => {
  if (summaryRate.value >= 100) return { type: 'danger' as const, text: '超支' }
  if (summaryRate.value >= 80) return { type: 'warning' as const, text: '预警' }
  return { type: 'success' as const, text: '正常' }
})

// ─── 工具方法 ────────────────────────────────────────────────────────────────
const getProgressColor = (rate: number): string => {
  if (rate >= 100) return '#EF4444'
  if (rate >= 80) return '#F59E0B'
  return '#16A34A'
}

const getPeriodText = (item: BudgetWithProgress): string => {
  if (item.period_type === 'yearly') return `${item.year}年`
  return `${item.year}年${item.month}月`
}

const statusTag = (status: string) => {
  const map: Record<string, { type: 'success' | 'warning' | 'danger'; text: string }> = {
    normal: { type: 'success', text: '正常' },
    warning: { type: 'warning', text: '预警' },
    exceeded: { type: 'danger', text: '超支' },
  }
  return map[status] ?? { type: 'success', text: '正常' }
}

// ─── 数据加载 ────────────────────────────────────────────────────────────────
const fetchData = async () => {
  loading.value = true
  try {
    const params = {
      year: queryForm.year,
      month: queryForm.month || undefined,
      period_type: queryForm.period_type || undefined,
    }
    const res = await getBudgets(params as any)
    budgets.value = res?.data?.budgets ?? []
  } catch {
    ElMessage.warning('加载预算数据失败，请检查网络或稍后重试')
    budgets.value = []
  } finally {
    loading.value = false
  }
}

const fetchCategories = async () => {
  categoryLoading.value = true
  try {
    const res = await getCategories({ type: 'expense' })
    expenseCategories.value = res?.data?.categories ?? []
  } catch {
    // 分类加载失败不影响主体功能
  } finally {
    categoryLoading.value = false
  }
}

// ─── 对话框操作 ─────────────────────────────────────────────────────────────
const openAddDialog = () => {
  dialogForm.id = 0
  dialogForm.period_type = 'monthly'
  dialogForm.year = currentYear
  dialogForm.month = currentMonth
  dialogForm.category_id = null
  dialogForm.amount = 1000
  dialogForm.alert_threshold = 80
  dialogVisible.value = true
}

const openEditDialog = (item: BudgetWithProgress) => {
  dialogForm.id = item.id
  dialogForm.period_type = item.period_type
  dialogForm.year = item.year
  dialogForm.month = item.month
  dialogForm.category_id = item.category_id
  dialogForm.amount = item.amount
  dialogForm.alert_threshold = item.alert_threshold
  dialogVisible.value = true
}

const handlePeriodTypeChange = () => {
  if (dialogForm.period_type === 'yearly') {
    dialogForm.month = undefined
  } else {
    dialogForm.month = currentMonth
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return

  submitting.value = true
  try {
    const payload = {
      period_type: dialogForm.period_type,
      year: dialogForm.year,
      month: dialogForm.period_type === 'monthly' ? dialogForm.month : undefined,
      category_id: dialogForm.category_id,
      amount: dialogForm.amount,
      alert_threshold: dialogForm.alert_threshold,
    }

    if (dialogForm.id) {
      await updateBudget(dialogForm.id, payload)
      ElMessage.success('预算更新成功')
    } else {
      await createBudget(payload as any)
      ElMessage.success('预算创建成功')
    }

    dialogVisible.value = false
    fetchData()
  } catch (err: unknown) {
    const msg = (err as { response?: { data?: { message?: string } } })?.response?.data?.message
    ElMessage.error(msg || '操作失败，请稍后重试')
  } finally {
    submitting.value = false
  }
}

const handleDelete = async (id: number) => {
  try {
    await deleteBudget(id)
    ElMessage.success('删除成功')
    fetchData()
  } catch {
    ElMessage.error('删除失败，请稍后重试')
  }
}

// ─── 生命周期 ────────────────────────────────────────────────────────────────
onMounted(() => {
  fetchData()
  fetchCategories()
})

watch(
  () => [queryForm.year, queryForm.month, queryForm.period_type],
  () => fetchData()
)
</script>

<style scoped>
.budget-page {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 页面标题 */
.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.page-title {
  margin: 0;
  font-size: 24px;
  font-weight: 700;
  color: #111827;
}

.header-actions {
  display: flex;
  gap: 12px;
}

/* 筛选卡片 */
.filter-card {
  border-radius: 12px;
  border: 1px solid #e5e7eb;
}

.filter-form {
  display: flex;
  flex-wrap: wrap;
  gap: 0;
}

:deep(.filter-form .el-form-item) {
  margin-bottom: 0;
  margin-right: 24px;
}

/* 汇总卡片 */
.summary-card {
  border-radius: 12px;
  border: 1px solid #e5e7eb;
}

.summary-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.summary-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #111827;
}

.overall-tag {
  font-weight: 500;
}

.summary-stats {
  display: flex;
  align-items: center;
  justify-content: space-around;
  margin-bottom: 20px;
  gap: 8px;
  flex-wrap: wrap;
}

.stat-item {
  text-align: center;
  flex: 1;
  min-width: 100px;
}

.stat-divider {
  width: 1px;
  height: 40px;
  background-color: #e5e7eb;
}

.stat-label {
  font-size: 13px;
  color: #6b7280;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 22px;
  font-weight: 700;
  color: #111827;
}

.stat-used {
  color: #F59E0B;
}

.stat-remaining {
  color: #16A34A;
}

.stat-exceeded {
  color: #EF4444;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 4px;
}

.exceeded-label {
  font-size: 12px;
  font-weight: 400;
  background-color: #fee2e2;
  color: #EF4444;
  padding: 1px 6px;
  border-radius: 4px;
}

.summary-progress {
  margin-top: 4px;
}

/* 状态条 */
.status-bar {
  display: flex;
  gap: 20px;
  align-items: center;
  padding: 0 4px;
}

.status-legend {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #6b7280;
}

.dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  display: inline-block;
}

.dot-normal { background-color: #16A34A; }
.dot-warning { background-color: #F59E0B; }
.dot-exceeded { background-color: #EF4444; }

/* 加载占位 */
.loading-placeholder {
  height: 200px;
}

/* 预算网格 */
.budget-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

/* 预算卡片 */
.budget-card {
  border-radius: 12px;
  border: 2px solid #e5e7eb;
  transition: box-shadow 0.2s, border-color 0.2s;
}

.budget-card:hover {
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
}

.budget-card.status-warning {
  border-color: #fcd34d;
}

.budget-card.status-exceeded {
  border-color: #fca5a5;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 14px;
  gap: 8px;
}

.card-category {
  display: flex;
  align-items: center;
  gap: 10px;
  min-width: 0;
}

.cat-icon {
  font-size: 24px;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background-color: #f3f4f6;
  border-radius: 8px;
  flex-shrink: 0;
}

.cat-info {
  min-width: 0;
}

.cat-name {
  font-size: 15px;
  font-weight: 600;
  color: #111827;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.cat-period {
  font-size: 12px;
  color: #9ca3af;
  margin-top: 2px;
}

.card-actions {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
}

.status-tag {
  font-size: 11px;
}

.card-amounts {
  font-size: 13px;
  color: #4b5563;
  margin-bottom: 10px;
  display: flex;
  align-items: baseline;
  gap: 4px;
}

.amount-used {
  font-weight: 600;
  color: #374151;
}

.amount-sep {
  color: #9ca3af;
}

.amount-total {
  color: #9ca3af;
}

.card-progress {
  margin-bottom: 8px;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
}

.rate-text {
  font-weight: 600;
}

.remaining-info {
  color: #9ca3af;
}

.exceeded-info {
  color: #EF4444;
  font-weight: 500;
}

/* 空状态 */
.empty-state {
  padding: 40px 0;
}

/* 对话框 */
.dialog-form {
  padding: 8px 0;
}

.threshold-row {
  display: flex;
  align-items: center;
  gap: 16px;
  width: 100%;
}

.threshold-label {
  width: 36px;
  text-align: right;
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  flex-shrink: 0;
}

.threshold-tip {
  font-size: 12px;
  color: #9ca3af;
  margin-top: 4px;
}

.cat-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

/* Element Plus 主题覆盖 */
:deep(.el-button--primary) {
  --el-button-bg-color: #16A34A;
  --el-button-border-color: #16A34A;
  --el-button-hover-bg-color: #15803D;
  --el-button-hover-border-color: #15803D;
  --el-button-active-bg-color: #166534;
  --el-button-active-border-color: #166534;
}

:deep(.el-progress-bar__inner) {
  transition: width 0.6s ease;
}

:deep(.el-card__body) {
  padding: 20px;
}
</style>
