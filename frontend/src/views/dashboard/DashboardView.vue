<template>
  <div class="dashboard-container">
    <div class="page-header">
      <h2>财务仪表盘</h2>
      <div class="actions">
        <el-date-picker
          v-model="currentDate"
          type="month"
          placeholder="选择月份"
          format="YYYY年MM月"
          value-format="YYYY-MM"
          size="default"
          :clearable="false"
          @change="handleMonthChange"
        />
      </div>
    </div>

    <!-- 概览卡片 -->
    <el-row :gutter="20" class="overview-cards">
      <el-col :span="6" :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="data-card income-card">
          <div class="card-content">
            <div class="card-icon">
              <el-icon><Wallet /></el-icon>
            </div>
            <div class="card-info">
              <div class="label">本月收入</div>
              <div class="value">¥ {{ Number(statistics.income || 0).toFixed(2) }}</div>
              <div class="trend positive">
                <el-icon><CaretTop /></el-icon> 12% 较上月
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6" :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="data-card expense-card">
          <div class="card-content">
            <div class="card-icon">
              <el-icon><Money /></el-icon>
            </div>
            <div class="card-info">
              <div class="label">本月支出</div>
              <div class="value">¥ {{ Number(statistics.expense || 0).toFixed(2) }}</div>
              <div class="trend negative">
                <el-icon><CaretBottom /></el-icon> 5% 较上月
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6" :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="data-card balance-card">
          <div class="card-content">
            <div class="card-icon">
              <el-icon><Histogram /></el-icon>
            </div>
            <div class="card-info">
              <div class="label">本月结余</div>
              <div class="value" :class="{ 'negative-val': statistics.balance < 0 }">
                ¥ {{ Number(statistics.balance || 0).toFixed(2) }}
              </div>
              <div class="trend normal">
                结余率 {{ ((Number(statistics.balance || 0) / Number(statistics.income || 1)) * 100).toFixed(1) }}%
              </div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="6" :xs="24" :sm="12" :md="6">
        <el-card shadow="hover" class="data-card asset-card">
          <div class="card-content">
            <div class="card-icon">
              <el-icon><House /></el-icon>
            </div>
            <div class="card-info">
              <div class="label">总资产</div>
              <div class="value">¥ {{ Number(statistics.totalAssets || 0).toFixed(2) }}</div>
              <div class="trend normal">包含所有账户</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 图表区域 -->
    <el-row :gutter="20" class="charts-row">
      <el-col :span="16" :xs="24">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>近期收支趋势</span>
              <el-radio-group v-model="trendPeriod" size="small">
                <el-radio-button value="week">本周</el-radio-button>
                <el-radio-button value="month">本月</el-radio-button>
              </el-radio-group>
            </div>
          </template>
          <div class="chart-container" ref="trendChartRef"></div>
        </el-card>
      </el-col>
      <el-col :span="8" :xs="24">
        <el-card shadow="hover" class="chart-card">
          <template #header>
            <div class="card-header">
              <span>支出分类占比</span>
            </div>
          </template>
          <div class="chart-container" ref="pieChartRef"></div>
        </el-card>
      </el-col>
    </el-row>

    <!-- 本月预算概览 -->
    <el-card shadow="hover" class="budget-overview-card">
      <template #header>
        <div class="card-header">
          <span>本月预算</span>
          <div class="budget-header-actions">
            <el-button link type="primary" size="small" @click="openBudgetDialog">
              <el-icon><Plus /></el-icon> 添加预算
            </el-button>
            <el-button link size="small" @click="$router.push('/budgets')">
              查看全部 <el-icon><ArrowRight /></el-icon>
            </el-button>
          </div>
        </div>
      </template>

      <div v-if="budgetLoading" class="budget-loading">
        <el-skeleton :rows="2" animated />
      </div>

      <div v-else-if="dashboardBudgets.length > 0" class="budget-list">
        <div
          v-for="item in dashboardBudgets"
          :key="item.id"
          class="budget-row"
        >
          <div class="budget-row__left">
            <span class="budget-icon">{{ item.category?.icon || '💰' }}</span>
            <span class="budget-name">{{ item.category?.name || '总预算' }}</span>
          </div>
          <div class="budget-row__right">
            <span class="budget-amounts">
              <span class="used">¥{{ Number(item.actual_spending).toFixed(0) }}</span>
              <span class="sep"> / </span>
              <span class="total">¥{{ Number(item.amount).toFixed(0) }}</span>
            </span>
            <span
              class="budget-rate"
              :style="{ color: getBudgetColor(item.percentage) }"
            >{{ item.percentage }}%</span>
          </div>
          <el-progress
            class="budget-progress"
            :percentage="Math.min(item.percentage, 100)"
            :color="getBudgetColor(item.percentage)"
            :stroke-width="6"
            :show-text="false"
          />
        </div>
      </div>

      <el-empty
        v-else
        description="本月暂无预算"
        :image-size="60"
        class="budget-empty"
      >
        <el-button size="small" type="primary" @click="openBudgetDialog">
          立即设置
        </el-button>
      </el-empty>
    </el-card>

    <!-- 快速操作 -->
    <el-card shadow="hover" class="quick-actions">
      <template #header>
        <div class="card-header">
          <span>常用功能</span>
        </div>
      </template>
      <div class="action-buttons">
        <el-button type="primary" size="large" :icon="Edit" @click="$router.push('/transactions/add')">记一笔</el-button>
        <el-button type="primary" size="large" :icon="DataLine" @click="$router.push('/statistics')">查看报表</el-button>
        <el-button type="primary" size="large" :icon="Upload" @click="$router.push('/import')">导入账单</el-button>
      </div>
    </el-card>

    <!-- 快速添加预算对话框 -->
    <el-dialog
      v-model="budgetDialogVisible"
      title="添加预算"
      width="440px"
      destroy-on-close
      align-center
    >
      <el-form
        ref="budgetFormRef"
        :model="budgetForm"
        :rules="budgetRules"
        label-width="90px"
      >
        <el-form-item label="周期类型" prop="period_type">
          <el-select
            v-model="budgetForm.period_type"
            style="width: 100%"
            @change="handlePeriodTypeChange"
          >
            <el-option label="月度预算" value="monthly" />
            <el-option label="年度预算" value="yearly" />
          </el-select>
        </el-form-item>

        <el-form-item label="年份" prop="year">
          <el-select v-model="budgetForm.year" style="width: 100%">
            <el-option
              v-for="y in availableYears"
              :key="y"
              :label="`${y}年`"
              :value="y"
            />
          </el-select>
        </el-form-item>

        <el-form-item
          v-if="budgetForm.period_type === 'monthly'"
          label="月份"
          prop="month"
        >
          <el-select v-model="budgetForm.month" placeholder="请选择月份" style="width: 100%">
            <el-option v-for="m in 12" :key="m" :label="`${m}月`" :value="m" />
          </el-select>
        </el-form-item>

        <el-form-item label="关联分类">
          <el-select
            v-model="budgetForm.category_id"
            placeholder="不选则为总体预算"
            clearable
            style="width: 100%"
          >
            <el-option
              v-for="cat in expenseCategories"
              :key="cat.id"
              :label="cat.name"
              :value="cat.id"
            />
          </el-select>
        </el-form-item>

        <el-form-item label="预算金额" prop="amount">
          <el-input-number
            v-model="budgetForm.amount"
            :min="0.01"
            :precision="2"
            :step="100"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="预警阈值">
          <div class="threshold-row">
            <el-slider
              v-model="budgetForm.alert_threshold"
              :step="5"
              :min="50"
              :max="100"
              style="flex: 1"
            />
            <span class="threshold-val">{{ budgetForm.alert_threshold }}%</span>
          </div>
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="budgetDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="budgetSubmitting" @click="handleBudgetSubmit">
          创建预算
        </el-button>
        <el-button link @click="$router.push('/budgets'); budgetDialogVisible = false">
          前往预算管理
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, nextTick, onUnmounted } from 'vue'
import {
  Wallet, Money, Histogram, House, CaretTop, CaretBottom,
  Edit, DataLine, Upload, Plus, ArrowRight
} from '@element-plus/icons-vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import * as echarts from 'echarts'
import dayjs from 'dayjs'
import { getBudgets, createBudget } from '@/api/budgets'
import { getCategories } from '@/api/categories'
import type { BudgetWithProgress, BudgetPeriodType } from '@/types/budget'
import type { Category } from '@/types/category'

// ─── 月份选择 ────────────────────────────────────────────────────────────────
const currentDate = ref(dayjs().format('YYYY-MM'))

const handleMonthChange = () => {
  loadBudgets()
}

// ─── 概览数据（暂用固定值，待后端接口就绪后替换） ─────────────────────────────
const statistics = reactive({
  income: 8500.00,
  expense: 3240.50,
  balance: 5259.50,
  totalAssets: 156000.00,
})

// ─── 图表 ────────────────────────────────────────────────────────────────────
const trendPeriod = ref('week')
const trendChartRef = ref<HTMLElement | null>(null)
const pieChartRef = ref<HTMLElement | null>(null)
let trendChart: echarts.ECharts | null = null
let pieChart: echarts.ECharts | null = null

const initCharts = () => {
  if (trendChartRef.value) {
    trendChart = echarts.init(trendChartRef.value)
    trendChart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true },
      xAxis: {
        type: 'category',
        boundaryGap: false,
        data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
      },
      yAxis: { type: 'value' },
      series: [
        {
          name: '支出',
          type: 'line',
          smooth: true,
          areaStyle: { opacity: 0.1 },
          data: [120, 132, 101, 134, 90, 230, 210],
          itemStyle: { color: '#f56c6c' },
        },
        {
          name: '收入',
          type: 'line',
          smooth: true,
          areaStyle: { opacity: 0.1 },
          data: [220, 182, 191, 234, 290, 330, 310],
          itemStyle: { color: '#16A34A' },
        },
      ],
    })
  }

  if (pieChartRef.value) {
    pieChart = echarts.init(pieChartRef.value)
    pieChart.setOption({
      tooltip: { trigger: 'item' },
      legend: { bottom: '0%', left: 'center' },
      series: [
        {
          name: '支出分类',
          type: 'pie',
          radius: ['40%', '70%'],
          avoidLabelOverlap: false,
          itemStyle: { borderRadius: 10, borderColor: '#fff', borderWidth: 2 },
          label: { show: false, position: 'center' },
          emphasis: { label: { show: true, fontSize: 16, fontWeight: 'bold' } },
          labelLine: { show: false },
          data: [
            { value: 1048, name: '餐饮' },
            { value: 735, name: '购物' },
            { value: 580, name: '交通' },
            { value: 484, name: '娱乐' },
            { value: 300, name: '其他' },
          ],
        },
      ],
    })
  }
}

const handleResize = () => {
  trendChart?.resize()
  pieChart?.resize()
}

// ─── 预算数据 ────────────────────────────────────────────────────────────────
const budgetLoading = ref(false)
const allBudgets = ref<BudgetWithProgress[]>([])

const dashboardBudgets = computed(() => allBudgets.value.slice(0, 5))

const getBudgetColor = (rate: number): string => {
  if (rate >= 100) return '#EF4444'
  if (rate >= 80) return '#F59E0B'
  return '#16A34A'
}

const loadBudgets = async () => {
  budgetLoading.value = true
  try {
    const [year, month] = currentDate.value.split('-').map(Number)
    const res = await getBudgets({ year, month, period_type: 'monthly' })
    allBudgets.value = res?.data?.budgets ?? []
  } catch {
    allBudgets.value = []
  } finally {
    budgetLoading.value = false
  }
}

// ─── 快速添加预算对话框 ───────────────────────────────────────────────────────
const budgetDialogVisible = ref(false)
const budgetSubmitting = ref(false)
const budgetFormRef = ref<FormInstance>()
const expenseCategories = ref<Category[]>([])

const currentYear = dayjs().year()
const currentMonth = dayjs().month() + 1

const availableYears = computed(() =>
  Array.from({ length: 5 }, (_, i) => currentYear - i + 1)
)

const budgetForm = reactive({
  period_type: 'monthly' as BudgetPeriodType,
  year: currentYear,
  month: currentMonth as number | undefined,
  category_id: null as number | null,
  amount: 1000,
  alert_threshold: 80,
})

const budgetRules: FormRules = {
  period_type: [{ required: true, message: '请选择周期类型', trigger: 'change' }],
  year: [{ required: true, message: '请选择年份', trigger: 'change' }],
  amount: [
    { required: true, message: '请输入预算金额', trigger: 'blur' },
    {
      validator: (_rule, value, callback) => {
        if (!value || value <= 0) callback(new Error('预算金额必须大于 0'))
        else callback()
      },
      trigger: 'blur',
    },
  ],
}

const openBudgetDialog = () => {
  budgetForm.period_type = 'monthly'
  budgetForm.year = currentYear
  budgetForm.month = currentMonth
  budgetForm.category_id = null
  budgetForm.amount = 1000
  budgetForm.alert_threshold = 80
  budgetDialogVisible.value = true
  loadExpenseCategories()
}

const handlePeriodTypeChange = () => {
  budgetForm.month = budgetForm.period_type === 'monthly' ? currentMonth : undefined
}

const loadExpenseCategories = async () => {
  if (expenseCategories.value.length > 0) return
  try {
    const res = await getCategories({ type: 'expense' })
    expenseCategories.value = res?.data?.categories ?? []
  } catch {
    // 分类加载失败不影响主体流程
  }
}

const handleBudgetSubmit = async () => {
  if (!budgetFormRef.value) return
  const valid = await budgetFormRef.value.validate().catch(() => false)
  if (!valid) return

  budgetSubmitting.value = true
  try {
    await createBudget({
      period_type: budgetForm.period_type,
      year: budgetForm.year,
      month: budgetForm.period_type === 'monthly' ? budgetForm.month : undefined,
      category_id: budgetForm.category_id,
      amount: budgetForm.amount,
      alert_threshold: budgetForm.alert_threshold,
    } as any)
    ElMessage.success('预算创建成功')
    budgetDialogVisible.value = false
    loadBudgets()
  } catch (err: unknown) {
    const msg = (err as { response?: { data?: { message?: string } } })?.response?.data?.message
    ElMessage.error(msg || '创建失败，请稍后重试')
  } finally {
    budgetSubmitting.value = false
  }
}

// ─── 生命周期 ────────────────────────────────────────────────────────────────
onMounted(() => {
  nextTick(() => {
    initCharts()
    window.addEventListener('resize', handleResize)
  })
  loadBudgets()
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  trendChart?.dispose()
  pieChart?.dispose()
})
</script>

<style scoped>
.dashboard-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

/* 标题栏 */
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

/* 概览卡片 */
.data-card {
  height: 140px;
}

.card-content {
  display: flex;
  align-items: center;
  height: 100%;
}

:deep(.el-card__body) {
  padding: 20px;
  height: 100%;
  box-sizing: border-box;
}

.card-icon {
  width: 56px;
  height: 56px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 20px;
  font-size: 28px;
  flex-shrink: 0;
}

.income-card .card-icon  { background-color: #f0fdf4; color: #16A34A; }
.expense-card .card-icon { background-color: #fef0f0; color: #EF4444; }
.balance-card .card-icon { background-color: #f3f4f6; color: #6b7280; }
.asset-card .card-icon   { background-color: #eff6ff; color: #3b82f6; }

.card-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.label {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 8px;
}

.value {
  font-size: 24px;
  font-weight: 600;
  color: #111827;
  margin-bottom: 4px;
  line-height: 1.2;
}

.negative-val { color: #EF4444; }

.trend {
  font-size: 12px;
  display: flex;
  align-items: center;
  gap: 2px;
}
.trend.positive { color: #16A34A; }
.trend.negative { color: #EF4444; }
.trend.normal   { color: #9ca3af; }

/* 图表 */
.charts-row { margin-top: 0; }

.chart-card { margin-bottom: 0; }

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-container {
  height: 300px;
  width: 100%;
}

/* 预算概览卡片 */
.budget-overview-card {
  border-radius: 12px;
  border: 1px solid #e5e7eb;
}

.budget-header-actions {
  display: flex;
  align-items: center;
  gap: 4px;
}

.budget-loading {
  padding: 8px 0;
}

.budget-list {
  display: flex;
  flex-direction: column;
  gap: 14px;
}

.budget-row {
  display: grid;
  grid-template-columns: 1fr auto;
  grid-template-rows: auto auto;
  column-gap: 12px;
  row-gap: 6px;
  align-items: center;
}

.budget-row__left {
  display: flex;
  align-items: center;
  gap: 8px;
}

.budget-icon {
  font-size: 18px;
  line-height: 1;
}

.budget-name {
  font-size: 14px;
  font-weight: 500;
  color: #374151;
}

.budget-row__right {
  display: flex;
  align-items: center;
  gap: 10px;
}

.budget-amounts {
  font-size: 13px;
}

.budget-amounts .used {
  font-weight: 600;
  color: #374151;
}

.budget-amounts .sep {
  color: #d1d5db;
}

.budget-amounts .total {
  color: #9ca3af;
}

.budget-rate {
  font-size: 13px;
  font-weight: 600;
  min-width: 36px;
  text-align: right;
}

.budget-progress {
  grid-column: 1 / -1;
}

.budget-empty {
  padding: 16px 0;
}

/* 快速操作 */
.quick-actions .action-buttons {
  display: flex;
  gap: 15px;
  flex-wrap: wrap;
}

/* 预算对话框 */
.threshold-row {
  display: flex;
  align-items: center;
  gap: 16px;
  width: 100%;
}

.threshold-val {
  width: 36px;
  text-align: right;
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  flex-shrink: 0;
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
  transition: width 0.5s ease;
}
</style>
